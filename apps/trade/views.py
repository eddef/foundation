import json
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.views.generic import View
from django.forms.models import model_to_dict
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from djangular.views.mixins import JSONResponseMixin, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from django.conf import settings
from apps.utils import utils
from models import *
import forms
import serializers

def ng_trade(request):
    return render(request, 'ng-trade.html')

class MerchantDetail(generics.RetrieveAPIView):
    queryset = Merchant.objects.all()
    serializer_class = serializers.MerchantSerializer

class CategoryList(APIView):

    def get(self, request, merchant_type=None):
        categories = Category.objects.filter(parent_category__isnull=True)

        if merchant_type == 'validated':
            serializer = serializers.CategoryValidatedSerializer(categories)
        elif merchant_type == 'candidates':
            serializer = serializers.CategoryCandidatesSerializer(categories)
        elif merchant_type == 'blocked':
            serializer = serializers.CategoryBlockedSerializer(categories)
        else:
            serializer = serializers.CategorySerializer(categories)
            
        return Response(serializer.data)

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

class EditMerchant(APIView):

    def commonSave(self, request, serializer):
        serializer.save()

    def put(self, request, pk):

        mer = get_object_or_404(Merchant, pk=pk)
        if (not request.user.has_perm("trade.change_merchant")
            and mer.user != request.user):
            return HttpResponseForbidden()

        data = request.DATA
        data['user'] = mer.user.id
        serializer = serializers.MerchantSerializer(mer, data=data)
        if serializer.is_valid():
            
            mer = serializer.save()
            mer.save()
            # mer.email = request.user.email
            # send_new_mer_mails(mer)

            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            msg = "Thank you for submitting your request. It will be validated by a human soon."
            return Response({"Success: ": [msg]}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):

        data = request.DATA
        data['user'] = request.user.id
        serializer = serializers.MerchantSerializer(data=data)
        if serializer.is_valid():
            
            serializer.save()
            # mer.email = request.user.email
            # send_new_mer_mails(mer)

            # return Response(serializer.data, status=status.HTTP_201_CREATED)
            msg = "Thank you for submitting your request. It will be validated by a human soon."
            return Response({"Success: ": [msg]}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateMerchant(APIView):

    def put(self, request, pk):
        if not request.user.has_perm("trade.change_merchant"):
            return HttpResponseForbidden()
        mer = get_object_or_404(Merchant, pk=pk)
    
        if mer.validated_by:
            # Block merchant
            mer.validated_by = None
            mer.save()
        else:
            mer.validated_by = request.user
            if mer.validated:
                # Unblock merchant
                mer.save()
            else:
                # Validate merchant
                mer.validated = datetime.now()
                mer.save()

        serializer = serializers.MerchantSerializer(mer)
        return Response(serializer.data)
