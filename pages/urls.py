# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
	# O nome 'page_detail' é importante, usamos ele no template do menu!
	path('<slug:slug>/', views.page_detail, name='page_detail'),
]