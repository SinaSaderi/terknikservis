from django import forms
from users.models import User

from .models import Product


class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.get_full_name()


class ServiceForm(forms.ModelForm):
    user = CustomUserChoiceField(queryset=User.objects.all())

    class Meta:
        model = Product
        fields = '__all__'