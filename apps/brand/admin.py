from django.contrib import admin
from .models import Brand

class BrandAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(Brand, BrandAdmin)
