# blog/views.py
from django.shortcuts import render, get_object_or_404
from .models import Post
from menu_manager.models import MenuItem

# View para a lista de todos os posts
def post_list(request):
	posts = Post.objects.all() # Busca todos os objetos Post
	menu_items = MenuItem.objects.filter(parent__isnull=True).order_by('order')

	context = {
		'posts': posts,
		'menu_items': menu_items,
	}
	return render(request, 'blog/post_list.html', context)

# View para a página de detalhe de um único post
def post_detail(request, slug):
	post = get_object_or_404(Post, slug=slug) # Busca o post específico pela URL
	menu_items = MenuItem.objects.filter(parent__isnull=True).order_by('order')

	context = {
		'post': post,
		'menu_items': menu_items,
	}
	return render(request, 'blog/post_detail.html', context)