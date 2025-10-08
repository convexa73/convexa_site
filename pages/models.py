# pages/models.py
from django.db import models

class Page(models.Model):
	title = models.CharField(max_length=200, verbose_name="Título")
	slug = models.SlugField(max_length=200, unique=True, verbose_name="URL (atalho)")
	content = models.TextField(verbose_name="Conteúdo")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Modificação")

	class Meta:
		verbose_name = "Página"
		verbose_name_plural = "Páginas"

	def __str__(self):
		return self.title