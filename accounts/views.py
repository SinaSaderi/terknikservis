from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from apps.service.models import Service

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.filter(user=self.request.user)
        print(context['services'])
        return context

def detail(req, pk):
    service = Service.objects.get(pk=pk)
    total = 0

    for o in service.operations.all():
        total += o.amount

    for p in service.pieces.all():
        total += p.price

    print(total)

    context = {
        'service': service,
        'total': total
    }

    return render(req, 'accounts/detail.html', context)