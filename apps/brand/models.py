from django.db import models
from django.utils.translation import ugettext_lazy as _

class Brand(models.Model):
    title = models.CharField(verbose_name=_("Title"), max_length=255)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title
