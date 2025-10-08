# portfolio/views.py
from django.shortcuts import render, get_object_or_404
from .models import Project
from menu_manager.models import MenuItem

def project_list(request):
	# 1. Busca todos os projetos no banco de dados
	projects = Project.objects.all()

	# 2. Busca os itens do menu para exibir na navegação
	menu_items = MenuItem.objects.filter(parent__isnull=True).order_by('order')

	# 3. Prepara os dados para enviar ao template
	context = {
		'projects': projects,
		'menu_items': menu_items,
	}

	# 4. Renderiza a página HTML, passando os dados
	return render(request, 'portfolio/project_list.html', context)
	
# --- NOVA VIEW PARA O DETALHE DE UM PROJETO ---
def project_detail(request, slug):
	# Busca o projeto específico pela URL (slug), ou retorna erro 404
	project = get_object_or_404(Project, slug=slug)
	menu_items = MenuItem.objects.filter(parent__isnull=True).order_by('order')
	
	context = {
		'project': project,
		'menu_items': menu_items,
	}
	return render(request, 'portfolio/project_detail.html', context)