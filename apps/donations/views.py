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
from .fields import BitcoinAddressField
import forms

def ng_donations(request):
    return render(request, 'ng-donations.html', 
                  {'frc_explorer': settings.FRC_EXPLORER,
                   'btc_explorer': settings.BTC_EXPLORER})

class OrgListView(JSONResponseMixin, View):
    def get_organizations(self):
        orgs = Organization.objects.filter(validated_by__isnull=True)
        orgs_list = []
        for org in orgs:
            orgs_list.append(model_to_dict(org, fields=[], exclude=[]))
        return orgs_list

class OrgDetailView(JSONResponseMixin, View):
    # def get(self, request, *args, **kwargs):
    #     kwargs.update(action='get_organization')
    #     return super(OrgDetailView, self).get(self, request, *args, **kwargs)
    def get_organization(self, organization_id=None):
        org = Organization.objects.get(pk=self.kwargs['org_id'])
        return model_to_dict(org, fields=[], exclude=[])

def send_new_org_mails(org):
    context = {'org': org}

    admins = User.objects.filter(groups__name='donations_admin')
    if (admins.count() <= 0):
        admins = User.objects.filter(is_superuser=True)
    admin_mails = ""
    for user in admins:
        admin_mails += user.email + ', '
    # Remove the last ', '
    admin_mails = admin_mails[:-2]

    utils.send_html_mail('mail/admin_mail.html', context, 
                         "New organization registration: %s" % org.name, 
                         org.email,
                         admin_mails)

    utils.send_html_mail('mail/org_mail.html', context, 
                         "Thanks for registering your organization !", 
                         'noreply@freicoin.org', org.email)

@login_required
def org_edit(request, id=None, template_name='new_organiation.html'):

    if id:
        org = get_object_or_404(Organization, pk=id)
        if (not request.user.has_perm("donations.change_organization")
            and org.user != request.user):
            return HttpResponseForbidden()
    else:
        org = Organization(user=request.user)

    form = forms.OrganizationForm(request.POST or None, instance=org)

    if form.is_valid():

        org = form.save()
        org.save()

        cd = form.cleaned_data

        frc_addr = PaymentAddress()
        frc_addr.owner = org
        frc_addr.address = cd['freicoin_address']
        frc_addr.type = PaymentAddress.FREICOIN
        frc_addr.save()
        org.freicoin_address = frc_addr

        if cd['bitcoin_address']:
            btc_addr = PaymentAddress()
            btc_addr.owner = org
            btc_addr.address = cd['bitcoin_address']
            btc_addr.type = PaymentAddress.BITCOIN
            btc_addr.save()
            org.bitcoin_address = btc_addr

        org.save()

        send_new_org_mails(org)

        return redirect('org_thanks')

    return render(request, template_name, {'form': form})

def thanks(request):
    return render(request, 'thanks.html')
