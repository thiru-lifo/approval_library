from rest_framework import serializers
from django.db.models import CharField, Value, BooleanField
from django.db.models import Count, Case, When, IntegerField
from . import models
from master.serializer import (
    TrialUnitsSerializer,
)
from master import models as masterModels


class TrialUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = masterModels.TrialUnits
        fields = "__all__"


# Pages
class PagesListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)

    class Meta:
        model = models.Pages
        fields = "__all__"


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pages
        fields = "__all__"


# Sliders
class SlidersListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)

    class Meta:
        model = models.Sliders
        fields = "__all__"


class SlidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sliders
        fields = "__all__"


# contact-us
class ContactSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(format="%Y-%m-%d")
    trial_unit = TrialUnitsSerializer(read_only=True)

    class Meta:
        model = models.Contact
        fields = "__all__"
