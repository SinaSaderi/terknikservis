from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User
from apps.product.models import Product
from apps.status.models import Status


def safe_remove():
    return True

class Service(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET(safe_remove), related_name='customer', verbose_name=_("Customer"))
    product = models.ForeignKey(Product, on_delete=models.SET(safe_remove), related_name='product', verbose_name=_("Product"))
    serial_number = models.CharField(verbose_name=_("Serial number"), max_length=255, blank=True, null=True)
    model_number = models.CharField(verbose_name=_("Model number"), max_length=255, blank=True, null=True)
    delivery_date = models.DateField(verbose_name=_("Delivery date"), blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.SET(safe_remove), related_name='status', verbose_name=_("Status"))
    desc = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    def __str__(self):
        return "service str"

    __unicode__ = __str__

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

