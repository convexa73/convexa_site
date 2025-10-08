# menu_manager/models.py
from django.db import models

class MenuItem(models.Model):
	title = models.CharField(max_length=100, verbose_name="Título")
	# Vamos linkar para uma Página ou para uma URL externa
	page = models.ForeignKey(
		'pages.Page',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		verbose_name="Página de destino"
	)
	external_url = models.CharField(
		max_length=200,
		blank=True,
		verbose_name="Link externo (se não houver página)"
	)
	order = models.IntegerField(default=0, verbose_name="Ordem")
	parent = models.ForeignKey(
		'self',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='children',
		verbose_name="Menu Pai (para submenus)"
	)
	
	# --- ADICIONE ESTA LINHA ---
	open_in_new_tab = models.BooleanField(default=False, verbose_name="Abrir em nova aba?")

	class Meta:
		ordering = ['order']
		verbose_name = "Item de Menu"
		verbose_name_plural = "Itens de Menu"

	def __str__(self):
		return self.title