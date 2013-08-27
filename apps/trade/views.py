import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.views.generic import View
from django.forms.models import model_to_dict
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from djangular.views.mixins import JSONResponseMixin, HttpResponseBadRequest

from django.conf import settings
from apps.utils import utils
from models import *
import forms

def ng_trade(request):
    return render(request, 'ng-trade.html')

class MerchantListView(JSONResponseMixin, View):
    def get_merchants(self):
        mers = Merchant.objects.exclude(validated__isnull=True
                                            ).exclude(validated_by__isnull=True)
        mer_list = []
        for mer in mers:
            mer_list.append(model_to_dict(mer, fields=[], exclude=[]))
        return mer_list

class MerchantDetailView(JSONResponseMixin, View):
    # TODO remove this or merchant_id param and od the same in donations
    # def get(self, request, *args, **kwargs):
    #     kwargs.update(action='get_merchant')
    #     return super(MerchantDetailView, self).get(self, request, *args, **kwargs)
    def get_merchant(self, merchant_id=None):
        mer = Merchant.objects.get(pk=self.kwargs['mer_id'])
        return model_to_dict(mer, fields=[], exclude=[])

def send_new_mer_mails(mer):
    context = {'merchant': mer}

    admins = User.objects.filter(groups__name='trade_admin')
    if (admins.count() <= 0):
        admins = User.objects.filter(is_superuser=True)
    admin_mails = ""
    for user in admins:
        admin_mails += user.email + ', '
    # Remove the last ', '
    admin_mails = admin_mails[:-2]

    utils.send_html_mail('mail/admin_mail.html', context, 
                         "New merchant registration: %s" % mer.name, 
                         mer.email,
                         admin_mails)

    utils.send_html_mail('mail/merchant_mail.html', context, 
                         "Thanks for registering your business !", 
                         'noreply@freicoin.org', mer.email)

@login_required
def mer_edit(request, id=None, template_name='new_organiation.html'):

    if id:
        mer = get_object_or_404(Merchant, pk=id)
        if (not request.user.has_perm("trade.change_merchant")
            and mer.user != request.user):
            return HttpResponseForbidden()
    else:
        mer = Merchant(user=request.user)

    form = forms.MerchantForm(request.POST or None, instance=mer)

    if form.is_valid():

        mer = form.save()
        mer.save()

        mer.email = request.user.email
        send_new_mer_mails(mer)

        return redirect('mer_thanks')

    return render(request, template_name, {'form': form})

def thanks(request):
    return render(request, 'thanks.html')

