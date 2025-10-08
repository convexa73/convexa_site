# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
	# Rota para a lista de posts -> /blog/
	path('', views.post_list, name='post_list'),

	# Rota para o detalhe de um post -> /blog/meu-post/
	path('<slug:slug>/', views.post_detail, name='post_detail'),
]