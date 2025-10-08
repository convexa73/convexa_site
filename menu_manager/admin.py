# menu_manager/admin.py
from django.contrib import admin
from .models import MenuItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
	list_display = ('title', 'page', 'external_url', 'order', 'parent', 'open_in_new_tab')
	list_editable = ('order', 'parent', 'open_in_new_tab')