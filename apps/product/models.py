from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.brand.models import Brand

def safe_remove():
    return True

class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.SET(safe_remove), verbose_name=_("Brand"))
    title = models.CharField(verbose_name=_("Title"), max_length=255)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title
