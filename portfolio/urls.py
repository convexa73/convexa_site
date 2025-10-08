# portfolio/urls.py
from django.urls import path
from . import views

urlpatterns = [
	# Rota para a lista de projetos
	path('', views.project_list, name='project_list'),
	
	# --- NOVA ROTA PARA O DETALHE DE UM PROJETO ---
	# Ex: /portfolio/meu-primeiro-projeto/
	path('<slug:slug>/', views.project_detail, name='project_detail'),
]