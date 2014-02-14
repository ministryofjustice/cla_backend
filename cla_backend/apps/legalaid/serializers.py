from rest_framework import serializers

from .models import Category, EligibilityCheck, Property, Finance


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ('value', 'equity', 'share', 'id')

class FinanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Finance
        fields = (
            "bank_balance",
            "investment_balance",
            "asset_balance",
            "credit_balance",
            "earnings",
            "other_income",
            "self_employed"
        )


class EligibilityCheckSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(max_length=500, required=False)
    property_set = PropertySerializer(allow_add_remove=True, many=True, required=False)
    your_finances = FinanceSerializer(required=False)
    partner_finances = FinanceSerializer(required=False)

    class Meta:
        model = EligibilityCheck
        fields = (
            'reference',
            'category',
            'notes',
            'property_set',
            'your_finances',
            'partner_finances'
        )

