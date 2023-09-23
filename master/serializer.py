from socketserver import DatagramRequestHandler
from venv import create
from django.db.models import F
from rest_framework import serializers
from .models import Countries, States, Cities, LookupType, Lookup, Region
from access.serializer import AccessUserRoleserializer
from . import models


class Countriesserializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = "__all__"


class Regionserializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class ListRegionserializer(serializers.ModelSerializer):
    country = Countriesserializer(read_only=True)

    class Meta:
        model = Region
        fields = "__all__"


class ListStatesserializer(serializers.ModelSerializer):
    country = Countriesserializer(read_only=True)
    region = Regionserializer(read_only=True)

    class Meta:
        model = States
        fields = "__all__"


class Statesserializer(serializers.ModelSerializer):
    class Meta:
        model = States
        fields = "__all__"

    def required(value):
        if value is None:
            raise serializers.ValidationError("This field is required")


class ListCitiesserializer(serializers.ModelSerializer):
    state = Statesserializer(read_only=True)

    class Meta:
        model = Cities
        fields = "__all__"


class Citiesserializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = "__all__"


class LookupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookupType
        fields = "__all__"


class ListLookupSerializer(serializers.ModelSerializer):
    type = LookupTypeSerializer(read_only=True)

    class Meta:
        model = Lookup
        fields = "__all__"


class LookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lookup
        fields = "__all__"


class TrialUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TrialUnits
        fields = ("id", "name", "code", "description", "status")


class CommandListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Command
        fields = ("id", "name", "code", "description", "status")


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Command
        fields = ("id", "name", "code", "description", "status")


class SatelliteUnitsListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)
    command = CommandSerializer(read_only=True)

    class Meta:
        model = models.SatelliteUnits
        fields = "__all__"


class SatelliteUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SatelliteUnits
        fields = "__all__"


class SatelliteShipSerializer(serializers.ModelSerializer):
    satellite_unit = SatelliteUnitsSerializer(read_only=True)

    class Meta:
        model = models.ShipSatelliteMapping
        fields = "__all__"


# end
class ShipsListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)
    command = CommandSerializer(read_only=True)

    # satellite_unit = SatelliteUnitsSerializer(read_only=True)
    class Meta:
        model = models.Ships
        fields = (
            "id",
            "name",
            "code",
            "description",
            "status",
            "trial_unit",
            "command",
            "created_by",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["satellite_units"] = SatelliteShipSerializer(
            models.ShipSatelliteMapping.objects.filter(ship_id=response["id"]),
            many=True,
        ).data
        return response


class ShipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ships
        fields = (
            "id",
            "name",
            "code",
            "description",
            "status",
            "trial_unit",
            "command",
            "created_by",
        )


class SectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sections
        fields = "__all__"


class SectionsListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)
    satellite_unit = SatelliteUnitsSerializer(read_only=True)
    ship = ShipsSerializer(read_only=True)
    command = CommandSerializer(read_only=True)

    class Meta:
        model = models.Sections
        fields = "__all__"


class EquipmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipments
        fields = "__all__"


class EquipmentsListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)
    satellite_unit = SatelliteUnitsSerializer(read_only=True)
    ship = ShipsSerializer(read_only=True)
    section = SectionsSerializer(read_only=True)
    command = CommandSerializer(read_only=True)

    class Meta:
        model = models.Equipments
        fields = "__all__"


class BoilersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Boilers
        fields = "__all__"


class BoilersListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)
    satellite_unit = SatelliteUnitsSerializer(read_only=True)
    ship = ShipsSerializer(read_only=True)
    section = SectionsSerializer(read_only=True)
    command = CommandSerializer(read_only=True)

    class Meta:
        model = models.Boilers
        fields = "__all__"


class TrialTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TrialTypes
        fields = "__all__"


class TrialTypesListSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)

    # satellite_unit = SatelliteUnitsSerializer(read_only=True)
    # ship = ShipsSerializer(read_only=True)
    # section = SectionsSerializer(read_only=True)
    # equipment = EquipmentsSerializer(read_only=True)
    class Meta:
        model = models.TrialTypes
        fields = "__all__"


class DataAccessShipSerializer(serializers.ModelSerializer):
    ship = ShipsSerializer(read_only=True)

    class Meta:
        model = models.DataAccessShip
        fields = "__all__"


class DataAccessSerializerCRUD(serializers.ModelSerializer):
    class Meta:
        model = models.DataAccess
        fields = "__all__"


class DataAccessSerializer(serializers.ModelSerializer):
    trial_unit = TrialUnitsSerializer(read_only=True)
    satellite_unit = SatelliteUnitsSerializer(read_only=True)
    ship = ShipsSerializer(read_only=True)

    class Meta:
        model = models.DataAccess
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        data_access_id = response["id"]
        response["ships"] = DataAccessShipSerializer(
            models.DataAccessShip.objects.filter(data_access_id=data_access_id),
            many=True,
        ).data
        return response


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = "__all__"


class ListDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = "__all__"


class LandingpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Landingpage
        fields = "__all__"


class LandingSatMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LandingSatMapping
        fields = "__all__"


class ListLandingpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Landingpage
        fields = "__all__"

    def to_representation(self, instance, request=None):
        response = super().to_representation(instance)
        sat = models.LandingSatMapping.objects.values(
            "id", "satellite_unit", "url"
        ).filter(Landing_id=response["id"])
        response["satellite_data"] = sat
        return response
