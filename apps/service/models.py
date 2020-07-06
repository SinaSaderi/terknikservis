from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User
from apps.product.models import Product
from apps.status.models import Status
import datetime

def safe_remove():
    return True

class Service(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET(safe_remove), related_name='customer', verbose_name=_("Customer"))
    product = models.ForeignKey(Product, on_delete=models.SET(safe_remove), related_name='product', verbose_name=_("Product"))
    serial_number = models.CharField(verbose_name=_("Serial number"), max_length=255, blank=True, null=True)
    register_number = models.CharField(verbose_name=_("Register number"), max_length=255, blank=True, null=True)
    model = models.CharField(verbose_name=_("Model/Color"), max_length=255, blank=True, null=True)
    capacity = models.CharField(verbose_name=_("Capacity"), max_length=255, blank=True, null=True)
    imei_number = models.CharField(verbose_name=_("Imei number"), max_length=255, blank=True, null=True)
    warranty = models.BooleanField(verbose_name=_("Warranty"), default=0, blank=True, null=True)
    register_date = models.DateField(verbose_name=_("Register date"), blank=True, null=True)
    delivery_date = models.DateField(verbose_name=_("Delivery date"), blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.SET(safe_remove), related_name='status', verbose_name=_("Status"))
    init_comment = models.TextField(blank=True, null=True, verbose_name=_("Initial comment"))
    problem = models.TextField(blank=True, null=True, verbose_name=_("Problem"))
    created_at = models.DateField(_("Created at"), default=datetime.date.today)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + " #" + str(self.pk)

    __unicode__ = __str__

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")


class Operation(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET(safe_remove), related_name='operations', verbose_name=_("Service"))
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    amount = models.FloatField(verbose_name=_("Price"), default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Operation")
        verbose_name_plural = _("Operations")

    __unicode__ = __str__

class Piece(models.Model):
    service = models.ForeignKey(Service, on_delete=models.SET(safe_remove), related_name='pieces', verbose_name=_("Service"))
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    price = models.FloatField(verbose_name=_("Service amount"), default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Piece")
        verbose_name_plural = _("Pieces")

    __unicode__ = __str__
