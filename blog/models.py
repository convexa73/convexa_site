# blog/models.py
from django.db import models
from django.utils.text import slugify

class Post(models.Model):
	title = models.CharField(max_length=200, verbose_name="Título")
	slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL (atalho)")
	author = models.CharField(max_length=100, verbose_name="Autor")
	content = models.TextField(verbose_name="Conteúdo do Artigo", blank=True, null=True)
	cover_image = models.ImageField(
		upload_to='blog_covers/',
		blank=True,
		null=True,
		verbose_name="Imagem de Capa"
	)
	youtube_video_id = models.CharField(
		max_length=50,
		blank=True,
		null=True,
		verbose_name="ID do Vídeo no YouTube (Opcional)"
	)
	publication_date = models.DateTimeField(auto_now_add=True, verbose_name="Data de Publicação")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Modificação")

	class Meta:
		verbose_name = "Post"
		verbose_name_plural = "Posts"
		ordering = ['-publication_date']

	def __str__(self):
		return self.title

	# --- MÉTODO NOVO PARA OBTER A THUMBNAIL ---
	def get_thumbnail_url(self):
		if self.cover_image:
			return self.cover_image.url
		elif self.youtube_video_id:
			# Retorna a URL da thumbnail de alta qualidade do YouTube
			return f'https://img.youtube.com/vi/{self.youtube_video_id}/hqdefault.jpg'
		else:
			# Retorna uma imagem genérica se não houver nenhuma das anteriores
			return 'https://via.placeholder.com/480x270.png?text=Convexa'

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)