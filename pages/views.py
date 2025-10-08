# pages/views.py
from django.shortcuts import render, get_object_or_404
from .models import Page
from menu_manager.models import MenuItem

# NOVA VIEW PARA A HOMEPAGE
def home(request):
	# A lógica é simples: apenas buscamos os itens do menu
	menu_items = MenuItem.objects.filter(parent__isnull=True).order_by('order')
	context = {
		'menu_items': menu_items,
	}
	# E renderizamos o novo template home.html
	return render(request, 'home.html', context)

# A view page_detail continua a mesma
def page_detail(request, slug):
	# Busca a página específica pela 'slug', ou retorna erro 404 se não encontrar
	page = get_object_or_404(Page, slug=slug)

	# Busca todos os itens de menu para o cabeçalho
	menu_items = MenuItem.objects.filter(parent__isnull=True).order_by('order')

	# Cria o "contexto" - um dicionário com os dados a serem enviados ao template
	context = {
		'page': page,
		'menu_items': menu_items,
	}

	# Renderiza o template, passando os dados do contexto
	return render(request, 'pages/page_detail.html', context)