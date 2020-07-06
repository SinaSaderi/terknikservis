from django.contrib import admin
from .models import Service, Operation, Piece
from .forms import ServiceForm
from django.utils.translation import ugettext_lazy as _

class OperationInline(admin.TabularInline):
    model = Operation
    extra = 1


class PicesInline(admin.TabularInline):
    model = Piece
    extra = 1

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'product', 'status', 'delivery_date')
    form = ServiceForm

    inlines = [OperationInline, PicesInline]

    def user_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name
    user_full_name.short_description = _("Customer")
    user_full_name.admin_order_field = _("user")






admin.site.register(Service, ServiceAdmin)
