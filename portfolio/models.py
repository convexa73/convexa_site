# portfolio/models.py
from django.db import models
from django.utils.text import slugify

class Project(models.Model):
	title = models.CharField(max_length=200, verbose_name="Título")
	slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL (atalho)")
	description = models.TextField(verbose_name="Descrição")
	# Campo para upload de imagem. Requer a biblioteca Pillow.
	image = models.ImageField(upload_to='portfolio_images/', verbose_name="Imagem do Projeto")
	technologies = models.CharField(max_length=200, verbose_name="Tecnologias Usadas")
	project_url = models.URLField(blank=True, verbose_name="Link do Projeto")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

	class Meta:
		verbose_name = "Projeto"
		verbose_name_plural = "Projetos"
		ordering = ['-created_at']

	def __str__(self):
		return self.title

	# Gera a URL automaticamente a partir do título antes de salvar
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)