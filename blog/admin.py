# blog/admin.py
from django.contrib import admin
from .models import Post
from django.conf import settings
import google.generativeai as genai
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

if settings.GEMINI_API_KEY:
	genai.configure(api_key=settings.GEMINI_API_KEY)

# ... (a função clean_srt continua a mesma)
def clean_srt(srt_text):
	srt_text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', srt_text)
	srt_text = re.sub(r'^\d+$', '', srt_text, flags=re.MULTILINE)
	srt_text = re.sub(r'<[^>]+>', '', srt_text)
	return "\n".join(filter(None, srt_text.splitlines()))


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'publication_date', 'updated_at')
	list_filter = ('author', 'publication_date')
	search_fields = ('title', 'content')
	prepopulated_fields = {'slug': ('title',)}

	def save_model(self, request, obj, form, change):
		if obj.youtube_video_id and not obj.content:
			try:
				# Usando a API oficial do YouTube (que requer a conta de serviço)
				youtube = build('youtube', 'v3')
				video_request = youtube.videos().list(part='snippet', id=obj.youtube_video_id)
				video_response = video_request.execute()

				if not video_response.get('items'):
					raise Exception("Vídeo não encontrado com o ID fornecido.")

				snippet = video_response['items'][0]['snippet']
				video_title = snippet['title']
				video_description = snippet['description']

				# Usando a biblioteca do Gemini (que agora deve funcionar)
				# Vamos usar o 'gemini-pro' que é mais estável
				model = genai.GenerativeModel('gemini-pro')
				prompt = f"""
				Aja como um escritor de artigos de tecnologia para o blog 'Convexa IA'.
				Crie um post de blog informativo e bem estruturado sobre um vídeo com o seguinte título e descrição.
				Elabore sobre os pontos mencionados na descrição, adicione uma introdução atraente e uma boa conclusão.
				O artigo deve ser autônomo e fazer sentido sem o vídeo.

				Título do Vídeo: {video_title}
				---
				Descrição do Vídeo:
				{video_description}
				---
				"""

				response = model.generate_content(prompt)
				generated_text = response.text

				attribution = "\n\n---\n*Este artigo foi gerado por IA (Gemini) com base no título e descrição do vídeo.*"
				obj.content = generated_text + attribution

				if not obj.title:
					obj.title = video_title

				self.message_user(request, "O artigo foi gerado por IA com base nos detalhes do vídeo.")

			except HttpError as e:
				error_content = e.content.decode('utf-8')
				self.message_user(request, f"Erro na API do YouTube: {error_content}", level='ERROR')
			except Exception as e:
				self.message_user(request, f"Não foi possível gerar o resumo. Erro: {e}", level='ERROR')

		super().save_model(request, obj, form, change)