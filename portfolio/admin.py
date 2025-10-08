# portfolio/admin.py
from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ('title', 'technologies', 'created_at')
	# O slug será preenchido automaticamente a partir do título
	prepopulated_fields = {'slug': ('title',)}