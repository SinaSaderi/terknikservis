from django.contrib import admin
from .models import Service
from .forms import ServiceForm
from django.utils.translation import ugettext_lazy as _
# from django.forms import ModelForm, ModelChoiceField
# from users.models import User

# class CustomModelChoiceField(ModelChoiceField):
#      def label_from_instance(self, obj):
#          return "%s %s" % (obj.first_name, obj.last_name)

# class MyServiceAdminForm(ModelForm):
#     user = CustomModelChoiceField(queryset=User.objects.all()) 
#     class Meta:
#           model = Service

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'product', 'status', 'delivery_date')
    form = ServiceForm

    def user_full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name
    user_full_name.short_description = _("Customer")
    user_full_name.admin_order_field = _("user")






admin.site.register(Service, ServiceAdmin)
