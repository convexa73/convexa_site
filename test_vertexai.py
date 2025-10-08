# test_vertexai.py (VERSÃO CORRIGIDA E AUTÔNOMA)
import os
import json
import requests
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv
from pathlib import Path # <-- NOVA IMPORTAÇÃO

print("Iniciando o teste de diagnóstico do Vertex AI...")

# --- NOVA LÓGICA PARA ENCONTRAR AS CREDENCIAIS ---
# 1. Carrega as variáveis de ambiente do seu arquivo .env
load_dotenv()

# 2. Define o caminho base do projeto e o caminho para o arquivo de credenciais
BASE_DIR = Path(__file__).resolve().parent
credentials_path = os.path.join(BASE_DIR, 'google-credentials.json')

# 3. Verifica se o arquivo de credenciais existe
if not os.path.exists(credentials_path):
	raise FileNotFoundError(f"Arquivo de credenciais não encontrado em: {credentials_path}. Verifique o nome do arquivo.")

# 4. Define a variável de ambiente que a biblioteca do Google procura
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
print("Arquivo de credenciais configurado com sucesso.")
# --- FIM DA NOVA LÓGICA ---

try:
	# Pega o ID do projeto do ambiente
	gcp_project_id = os.getenv('GCP_PROJECT_ID')
	if not gcp_project_id:
		raise ValueError("Erro: GCP_PROJECT_ID não encontrado no arquivo .env")

	print(f"ID do Projeto encontrado: {gcp_project_id}")

	# Autentica usando a variável de ambiente que acabamos de definir
	print("Autenticando com a Conta de Serviço...")
	credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
	auth_req = google.auth.transport.requests.Request()
	credentials.refresh(auth_req)
	access_token = credentials.token
	print("Autenticação bem-sucedida. Token de acesso obtido.")

	# O resto do script continua exatamente o mesmo...
	url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{gcp_project_id}/locations/us-central1/publishers/google/models/gemini-1.0-pro:generateContent"
	headers = { "Authorization": f"Bearer {access_token}", "Content-Type": "application/json", }
	data = { "contents": [{"parts": [{"text": "Isso é um teste. Diga 'Olá, Mundo!'."}]}] }

	print(f"Enviando requisição para: {url}")
	response = requests.post(url, headers=headers, json=data)

	print(f"\nStatus da Resposta: {response.status_code}")
	print("--- Resposta do Servidor ---")
	print(response.json())
	print("--------------------------")

	if response.status_code == 200:
		print("\nResultado: SUCESSO! A conexão e a permissão estão funcionando.")
	else:
		print(f"\nResultado: FALHA! O servidor respondeu com um erro {response.status_code}.")

except Exception as e:
	print(f"\nOcorreu um erro CRÍTICO durante o teste: {e}")