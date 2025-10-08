# pages/admin.py
from django.contrib import admin
from .models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'updated_at')
	prepopulated_fields = {'slug': ('title',)} # Preenche a URL automaticamente