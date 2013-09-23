from rest_framework import serializers

from .models import *

class MerchantSerializer(serializers.ModelSerializer):
    category_name = serializers.Field(source='category.name')
    owner = serializers.Field(source='user.username')
    validated_by = serializers.Field(source='validated_by.username')
    validated = serializers.Field(source='validated')

    class Meta:
        model = Merchant
        fields = ('id', 'name', 'website', 'category', 'category_name', 'user', 'owner',
                  'short_description', 'long_description', 'validated', 'validated_by')

class MerchantShortSerializer(serializers.ModelSerializer):
    category_name = serializers.Field(source='category.name')
    user = serializers.Field(source='user.username')

    class Meta:
        model = Merchant
        fields = ('id', 'name', 'website', 'short_description')

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    merchants = MerchantShortSerializer(source='merchants')

    class Meta:
        model = Category
        fields = ('id', 'name', 'merchants', 'child_categories')

CategorySerializer.base_fields['child_categories'] = CategorySerializer()

class CategoryValidatedSerializer(serializers.HyperlinkedModelSerializer):
    merchants = MerchantShortSerializer(source='validated')
    inner_merchants = serializers.Field(source='inner_validated')

    class Meta:
        model = Category
        fields = ('id', 'name', 'inner_merchants', 'merchants', 'child_categories')

CategoryValidatedSerializer.base_fields['child_categories'] = CategoryValidatedSerializer()

class CategoryCandidatesSerializer(serializers.HyperlinkedModelSerializer):
    merchants = MerchantShortSerializer(source='candidates')
    inner_merchants = serializers.Field(source='inner_candidates')

    class Meta:
        model = Category
        fields = ('id', 'name', 'inner_merchants', 'merchants', 'child_categories')

CategoryCandidatesSerializer.base_fields['child_categories'] = CategoryCandidatesSerializer()

class CategoryBlockedSerializer(serializers.HyperlinkedModelSerializer):
    merchants = MerchantShortSerializer(source='blocked')
    inner_merchants = serializers.Field(source='inner_blocked')

    class Meta:
        model = Category
        fields = ('id', 'name', 'inner_merchants', 'merchants', 'child_categories')

CategoryBlockedSerializer.base_fields['child_categories'] = CategoryBlockedSerializer()
