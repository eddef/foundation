import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.views.generic import View
from django.forms.models import model_to_dict

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from djangular.views.mixins import JSONResponseMixin, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from apps.utils import utils
from models import *
from .fields import BitcoinAddressField
import forms
import serializers

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategoryShortSerializer

class CategoryTree(APIView):

    def get(self, request, organization_type=None):
        categories = Category.objects.filter(parent_category__isnull=True)

        if organization_type == 'validated':
            serializer = serializers.CategoryValidatedSerializer(categories)
        elif organization_type == 'candidates':
            serializer = serializers.CategoryCandidatesSerializer(categories)
        elif organization_type == 'blocked':
            serializer = serializers.CategoryBlockedSerializer(categories)
        else:
            serializer = serializers.CategorySerializer(categories)
            
        return Response(serializer.data)

class OrganizationDetail(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer

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

    form = forms.OrganizationForm(request.POST or None, instance=org,
                                  initial={'freicoin_address': org.freicoin_address_value,
                                           'bitcoin_address': org.bitcoin_address_value})

    if form.is_valid():

        org = form.save()
        org.save()

        cd = form.cleaned_data

        if cd['freicoin_address'] != org.freicoin_address_value:
            frc_addr = PaymentAddress()
            frc_addr.address = cd['freicoin_address']
            frc_addr.owner = org
            frc_addr.type = PaymentAddress.FREICOIN
            frc_addr.save()
            org.freicoin_address = frc_addr

        if cd['bitcoin_address'] != org.bitcoin_address_value:
            btc_addr = PaymentAddress()
            btc_addr.address = cd['bitcoin_address']
            btc_addr.owner = org
            btc_addr.type = PaymentAddress.BITCOIN
            btc_addr.save()
            org.bitcoin_address = btc_addr

        org.save()
        send_new_org_mails(org)

        msg = "Thank you for submitting your request. It will be validated by a human soon."
        return render(request, 'messages_list.html', {'messages': [msg]})

    return render(request, template_name, {'form': form})

@login_required
def org_validate(request, id=None):
    if not request.user.has_perm("donations.change_organization"):
        return HttpResponseForbidden()
    org = get_object_or_404(Organization, pk=id)
    
    if org.validated_by:
        org.validated_by = None
        org.save()
        msg = "Organization %s has been invalidated." % org.name
    else:
        org.validated_by = request.user
        if org.validated:
            org.save()
            msg = "Organization %s is valid again." % org.name
        else:
            org.validated = datetime.now()
            org.save()
            msg = "Organization %s has been validated." % org.name

    return render(request, 'messages_list.html', {'messages': [msg]})
