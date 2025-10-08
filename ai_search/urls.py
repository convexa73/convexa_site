from django.urls import path
from . import views

urlpatterns = [
    path('', views.ia_hub, name='ia_hub'),                # /ia/
    path('api/chat/', views.chat_api, name='ia_chat_api') # /ia/api/chat/
]
