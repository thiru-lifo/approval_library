import code
from functools import partial
import json
from queue import Empty
from unicodedata import name
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

# from rest_framework import authentication, AllowAny
# from rest_framework.permissions import Is_Authenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import Http404
from functools import reduce
import operator
from django.db.models import Q

from .models import (
    Countries,
    LandingSatMapping,
    States,
    Cities,
    LookupType,
    Lookup,
    Region,
    ShipSatelliteMapping,
    DataAccess,
)

from .serializer import (
    Citiesserializer,
    CommandListSerializer,
    CommandSerializer,
    Countriesserializer,
    LandingSatMappingSerializer,
    ListCitiesserializer,
    Statesserializer,
    ListStatesserializer,
    LookupTypeSerializer,
    ListLookupSerializer,
    LookupSerializer,
    Regionserializer,
    ListRegionserializer,
    TrialUnitsSerializer,
    SatelliteUnitsSerializer,
    ShipsSerializer,
    SectionsSerializer,
    EquipmentsSerializer,
    TrialTypesSerializer,
    SatelliteUnitsListSerializer,
    ShipsListSerializer,
    SectionsListSerializer,
    EquipmentsListSerializer,
    TrialTypesListSerializer,
    BoilersSerializer,
    BoilersListSerializer,
)
from NavyTrials import language, error
from access.views import Common
from django.db.models import Count

from . import models
from . import serializer as cSerializer

# from Glosys import error

from django.db.models.functions import TruncMonth
from django.db.models import Count


class CountriesViews(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = Countries.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = Countriesserializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except Countries.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Country"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = Countries.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = Countriesserializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class CountriesDetailViews(APIView):
    def get_object(self, pk):
        try:
            return Countries.objects.get(pk=pk)
        except Countries.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        data1 = Countries.objects.all()

        # if not name in data1:
        #     return Response({"status" :error.context['error_code'],"message":"name"+language.context[language.defaultLang]['required'] }, status=status.HTTP_200_OK)
        # else:

        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "phone_code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "phone_code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "currency" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Currency"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip

                if not pk:
                    duplicate_code = (
                        Countries.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        Countries.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = Countriesserializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New country"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            Countries.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            Countries.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )

                    list = self.get_object(pk)

                    saveserialize = Countriesserializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Country"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class StatesViews(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q

        try:
            if pk:
                list = States.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = ListStatesserializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except States.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "State"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = States.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = ListStatesserializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class StatesDetailViews(APIView):
    def get_object(self, pk):
        try:
            return States.objects.get(pk=pk)
        except States.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "country" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Country"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "region" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Region"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )
            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip

                if not pk:
                    duplicate_code = (
                        States.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )
                    duplicate_name = (
                        States.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = Statesserializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New state"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            States.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            States.objects.values("name")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )

                    list = self.get_object(pk)

                    saveserialize = Statesserializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "State"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class CityViews(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q

        try:
            if pk:
                list = Cities.objects.filter(pk=pk).exclude(status="3").get()
                serialize = ListCitiesserializer(list)
                return Response(
                    {"status": error.context["success_code"], "data": serialize.data},
                    status=status.HTTP_200_OK,
                )

        except Cities.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "City"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = Cities.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = ListCitiesserializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class CityDetailViews(APIView):
    def get_object(self, pk):
        try:
            return Cities.objects.get(pk=pk)

        except Cities.DoesNotExist:
            # return Response(status=status.HTTP_404_NOT_FOUND)
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "state" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "State"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )
            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip

                if not pk:
                    duplicate_code = (
                        Cities.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )
                    duplicate_name = (
                        Cities.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = Citiesserializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New city"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )

                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )
                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            Cities.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )

                        duplicate_name = (
                            Cities.objects.values("name")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )

                    list = self.get_object(pk)
                    saveserialize = Citiesserializer(
                        list, data=request.data, partial=True
                    )

                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "City"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )

            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class RegionViews(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = Region.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = ListRegionserializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except Region.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Region"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = Region.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = ListRegionserializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class RegionDetailViews(APIView):
    def get_object(self, pk):
        try:
            return Region.objects.get(pk=pk)
        except Region.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "country" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Country"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )
            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip

                if not pk:
                    duplicate_code = (
                        Region.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )
                    duplicate_name = (
                        Region.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = Regionserializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New region"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            Region.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            Region.objects.values("name")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )

                    list = self.get_object(pk)

                    saveserialize = Regionserializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Region"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class LookupTypeViews(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q

        try:
            if pk:
                list = LookupType.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = LookupTypeSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except LookupType.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Lookup Type"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = LookupType.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = LookupTypeSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class LookupTypeDetailViews(APIView):
    def get_object(self, pk):
        try:
            return LookupType.objects.get(pk=pk)

        except LookupType.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "description" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Description"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )
            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip

                if not pk:
                    duplicate_code = (
                        LookupType.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )
                    duplicate_name = (
                        LookupType.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = LookupTypeSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New lookup type"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            LookupType.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            LookupType.objects.values("name")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )

                    list = self.get_object(pk)
                    saveserialize = LookupTypeSerializer(
                        list, data=request.data, partial=True
                    )

                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Lookup Type"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class LookupViews(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = Lookup.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = ListLookupSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except Lookup.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Lookup value"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = Lookup.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = ListLookupSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class LookupDetailViews(APIView):
    def get_object(self, pk):
        try:
            return Lookup.objects.get(pk=pk)

        except Lookup.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "type" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Type"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "description" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Description"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )

        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )
            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip

                if not pk:
                    duplicate_code = (
                        Lookup.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )
                    duplicate_name = (
                        Lookup.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )
                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )
                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        saveserialize = LookupSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New lookup value"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            Lookup.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            Lookup.objects.values("name")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )

                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )

                    list = self.get_object(pk)
                    saveserialize = LookupSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Lookup value"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class TrialUnitsList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.TrialUnits.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = serializer.TrialUnitsSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.TrialUnits.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial unit"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.TrialUnits.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]
        if "Authorized-Role" in request.headers:
            role_code = request.headers["Authorized-Role"]
            if role_code != "admin":
                satList = DataAccess.objects.values("trial_unit_id").filter(
                    user_id=request.user.id
                )
                ids = (o["trial_unit_id"] for o in satList)
                lists = lists.filter(id__in=ids)

        serializer = TrialUnitsSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class TrialUnitsCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.TrialUnits.objects.get(pk=pk)
        except models.TrialUnits.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.TrialUnits.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.TrialUnits.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = TrialUnitsSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New trial unit"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.TrialUnits.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.TrialUnits.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = TrialUnitsSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Trial Units"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class SatelliteUnitsList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()

        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                lists = (
                    models.SatelliteUnits.objects.filter(pk=pk)
                    .exclude(status="3")
                    .get()
                )
                if "Authorized-Role" in request.headers:
                    role_code = request.headers["Authorized-Role"]
                    # print(request.user.id)
                    if role_code != "admin":
                        list.filter(
                            id__in=DataAccess.objects.values(
                                "satellite_unit_id"
                            ).filter(user_id=request.user.id)
                        )
                serializeobj = SatelliteUnitsListSerializer(lists)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.SatelliteUnits.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Satellite unit"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.SatelliteUnits.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        if "Authorized-Role" in request.headers:
            role_code = request.headers["Authorized-Role"]
            if role_code != "admin":
                satList = DataAccess.objects.values("satellite_unit_id").filter(
                    user_id=request.user.id
                )
                ids = (o["satellite_unit_id"] for o in satList)
                lists = lists.filter(id__in=ids)

        serializer = SatelliteUnitsListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class SatelliteUnitsCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.SatelliteUnits.objects.get(pk=pk)
        except models.SatelliteUnits.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "trial_unit" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial unit"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.SatelliteUnits.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.SatelliteUnits.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = SatelliteUnitsSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New satellite unit"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.SatelliteUnits.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.SatelliteUnits.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = SatelliteUnitsSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Satellite unit"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class ShipsList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        satellite_unit_id = request.GET.get("satellite_unit_id")
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if satellite_unit_id is not None:
                normal_values.pop("satellite_unit_id")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.Ships.objects.filter(pk=pk).exclude(status="3").get()
                if satellite_unit_id is not None:
                    list = list.filter(
                        id__in=(
                            ShipSatelliteMapping.objects.values("ship_id").filter(
                                satellite_unit_id=satellite_unit_id
                            )
                        )
                    )
                serializeobj = ShipsListSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Ships.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Ship"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        command_id=models.SatelliteUnits.objects.values("command_id").filter(
                    id=satellite_unit_id
                ).first()
        if(satellite_unit_id):
            command_id=command_id['command_id']
            # print("COMMAND ID : ",command_id)
            lists = models.Ships.objects.exclude(status="3").filter(command_id=command_id)
        else:
            lists = models.Ships.objects.exclude(status="3")
        # print(" satellite_unit_id ",satellite_unit_id,type(satellite_unit_id))
        if(satellite_unit_id =='5' or satellite_unit_id =='23' or satellite_unit_id =='24'):
            idshipcbiu=[143,229,237,263]
            lists = models.Ships.objects.exclude(status="3").filter(id__in=idshipcbiu,command_id=command_id)
            
        # if satellite_unit_id is not None:
        #     lists = lists.filter(
        #         id__in=(
        #             ShipSatelliteMapping.objects.values("ship_id").filter(
        #                 satellite_unit_id=satellite_unit_id
        #             )
        #         )
        #     )
        
        # print(normal_values,"ooooooooooooooooooooooooo")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        # if(normal_values["trial_unit_id"]):
        #     normal_values.pop('trial_unit_id')
        # if(normal_values['satellite_unit_id']):
        #     normal_values.pop('satellite_unit_id')
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]
        # satList=''
        # ships=''
        if "Authorized-Role" in request.headers:
            role_code = request.headers["Authorized-Role"]
            if role_code != "admin":
                shipList = models.DataAccessShip.objects.values("ship_id").filter(
                    data_access__user_id=request.user.id
                )
                if satellite_unit_id:
                    shipList = shipList.values("ship_id").filter(
                        data_access__satellite_unit_id=satellite_unit_id
                    )
                ship_ids = (o["ship_id"] for o in shipList)

                lists = lists.filter(id__in=ship_ids)

        serializer = ShipsListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class ShipsCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Ships.objects.get(pk=pk)
        except models.Ships.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.Ships.objects.values("code")
                        .filter(
                            code=request.data["code"],
                            #trial_unit_id=request.data["trial_unit"],
                        )
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.Ships.objects.values("name")
                        .filter(
                            name=request.data["name"],
                            #trial_unit_id=request.data["trial_unit"],
                        )
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = ShipsSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            # if request.data["satellite_unit"]:
                            #     ShipSatelliteMapping.objects.filter(
                            #         ship_id=saveserialize.data["id"]
                            #     ).delete()
                            #     for id in request.data["satellite_unit"]:
                            #         ShipSatelliteMapping.objects.create(
                            #             satellite_unit_id=id,
                            #             ship_id=saveserialize.data["id"],
                            #         )
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New ship"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.Ships.objects.values("code")
                            .filter(
                                code=request.data["code"],
                                #trial_unit_id=request.data["trial_unit"],
                            )
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.Ships.objects.values("id", "name", "status")
                            .filter(
                                name=request.data["name"],
                                #trial_unit_id=request.data["trial_unit"],
                            )
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = ShipsSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        ShipSatelliteMapping.objects.filter(
                            ship_id=saveserialize.data["id"]
                        ).delete()
                        # if request.data["status"] == 1:
                        #     if request.data["satellite_unit"]:
                        #         for id in request.data["satellite_unit"]:
                        #             ShipSatelliteMapping.objects.create(
                        #                 satellite_unit_id=id,
                        #                 ship_id=saveserialize.data["id"],
                        #             )
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Ship"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        print("Serializer not valid")
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class SectionsList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.Sections.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = SectionsListSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Sections.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Section"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        # lists = models.Sections.objects.exclude(status="3")
        lists = models.Sections.objects.values(
            "id",
            "name",
            "code",
            "description",
            "status",
            "trial_unit__id",
            "trial_unit__name",
            "command__id",
            "command__name",
            "satellite_unit__id",
            "satellite_unit__name",
            "ship__id",
            "ship__name",
        ).exclude(status="3")
        code_in = models.SectionTrialUnitMapping.objects.values("section_code").filter(
            trial_unit__id=request.GET.get("trial_unit_id")
        )
        # print("code_in", code_in)
        # section = models.Sections.objects.values("id", "code").filter(
        #     trial_unit__id=request.GET.get("trial_unit_id"),
        #     ship__id=request.GET.get("ship_id"),
        # )
        # print("section", section)
        # for sec_code in code_in:
        #     mapped = lists.filter(
        #         trial_unit__id=request.GET.get("trial_unit_id"),
        #         code=sec_code["section_code"],
        #     )

        # for sec_id in mapped:
        #     lists = lists.filter(code=sec_id["code"])

        print("normal_values : ",normal_values)
        print("array_values : ",array_values)
        if("trial_unit_id" in normal_values.keys()):
            normal_values.pop("trial_unit_id")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)
        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        # serializer = SectionsListSerializer(lists, many=True)
        return Response(
            {
                "status": error.context["success_code"],
                "data": lists,
                # "section_id": hlo,
                "mapped": code_in
            },
            status=status.HTTP_200_OK,
        )


class SectionsCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Sections.objects.get(pk=pk)
        except models.Sections.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.Sections.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.Sections.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = SectionsSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New section"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.Sections.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.Sections.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = SectionsSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Section"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class EquipmentsList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")
            searchFilter = request.GET.get('searchFilter') 

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")
            
            if searchFilter is not None:
                normal_values.pop("searchFilter")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.Equipments.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = EquipmentsListSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Equipments.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Equipments"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        # lists = models.Equipments.objects.exclude(status="3")
        lists = models.Equipments.objects.values(
            "id",
            "name",
            "code",
            "description",
            "status",
            "trial_unit__id",
            "trial_unit__name",
            "command__id",
            "command__name",
            "satellite_unit__id",
            "satellite_unit__name",
            "ship__id",
            "ship__name",
            "section__id",
            "section__name",
            "serial_no",
            "model",
        ).exclude(status="3")
        normal_values = {
            key: value for key, value in normal_values.items() if value != "null"
        }
        normal_values = {
            key: value for key, value in normal_values.items() if value != ""
        }
        #print("normal_values : ",normal_values)
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)
        
        if searchFilter:
            lists=lists.filter(Q(command__name__icontains=searchFilter) | Q(satellite_unit__name__icontains=searchFilter) | Q(section__name__icontains=searchFilter) | Q(code__icontains=searchFilter)| Q(model__icontains=searchFilter)| Q(name__icontains=searchFilter)| Q(ship__name__icontains=searchFilter) | Q(trial_unit__name__icontains=searchFilter))
            
        total_length=lists.count()
        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)
        
        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]
        if "Authorized-Role" in request.headers:
            role_code = request.headers["Authorized-Role"]
            if role_code != "admin":
                shipList = models.DataAccessShip.objects.values("ship_id").filter(
                    data_access__user_id=request.user.id
                )
                ship_ids = (o["ship_id"] for o in shipList)

                lists = lists.filter(ship_id__in=ship_ids)
        # serializer = EquipmentsListSerializer(lists, many=True)
        # serializer =models.Equipments.objects.values(
        #                                     "id",
        #                                     "name",
        #                                     "code",
        #                                     "description",
        #                                     "status",
        #                                     "trial_unit__id",
        #                                     "trial_unit__name",
        #                                     "command__id",
        #                                     "command__name",
        #                                     "satellite_unit__id",
        #                                     "satellite_unit__name",
        #                                     "ship__id",
        #                                     "ship__name",
        #                                     "section__id",
        #                                     "section__name",
        #                                     "serial_no",
        #                                     "model",
        #                                     )
        # serializer.append(lists)
        return Response(
            {"status": error.context["success_code"], "data": lists,"total_length":total_length},
            status=status.HTTP_200_OK,
        )


# count of equipments
class EquipmentsGraphData(APIView):
    def get(self, request):
        equipment_obj = (
            models.Equipments.objects.exclude(status="3")
            .annotate(month=TruncMonth("created_on"))
            .values("month")
            .annotate(total=Count("id"))
            .values("month", "total")
        )
        return Response({"status": status.HTTP_200_OK, "data": equipment_obj})


class EquipmentsCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Equipments.objects.get(pk=pk)
        except models.Equipments.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk or pk == "null":
                    duplicate_code = (
                        models.Equipments.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.Equipments.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = EquipmentsSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New equipment"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.Equipments.objects.values("code")
                            .filter(
                                code=request.data["code"],
                                section_id=request.data["section"],
                            )
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.Equipments.objects.values("id", "name", "status")
                            .filter(
                                name=request.data["name"],
                                section_id=request.data["section"],
                            )
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = EquipmentsSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Equipment"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


# Boiler
class BoilersList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.Boilers.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = BoilersListSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Boilers.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Boilers"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.Boilers.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = BoilersListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class BoilersListDemo(APIView):
    def get(self, request, pk=None):
        ids=['263','237','229','213']
        lists = models.Equipments.objects.exclude(status="3").filter(ship_id__in=ids)
        serializer = EquipmentsListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class BoilersCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Boilers.objects.get(pk=pk)
        except models.Boilers.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.Boilers.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.Boilers.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = BoilersSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New Boilers"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.Boilers.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.Boilers.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = BoilersSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Boilers"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


# Commend
class CommandList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.Command.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = CommandListSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Command.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Command"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.Command.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = CommandListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class CommandCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Command.objects.get(pk=pk)
        except models.Command.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.Command.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.Command.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = CommandSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New Command"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.Command.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.Command.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = CommandSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Command"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


# ------
class TrialTypesList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.TrialTypes.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = TrialTypesListSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.TrialTypes.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial type"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.TrialTypes.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = TrialTypesListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class TrialTypesCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.TrialTypes.objects.get(pk=pk)
        except models.TrialTypes.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.TrialTypes.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.TrialTypes.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = TrialTypesSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New trial types"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.TrialTypes.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.TrialTypes.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = TrialTypesSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Trial Type"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class DepartmentList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = models.Department.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = cSerializer.ListDepartmentSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Department.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial type"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.Department.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = cSerializer.ListDepartmentSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class DepartmentCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Department.objects.get(pk=pk)
        except models.Department.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk:
                    duplicate_code = (
                        models.Department.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.Department.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = cSerializer.DepartmentSerializer(
                            data=request.data
                        )
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New department"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.Department.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.Department.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = cSerializer.DepartmentSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Department"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


from django.db.models.functions import TruncMonth
from django.db.models import Count


class EquipmentsGraphData(APIView):
    def get(self, request):
        equipment_obj = (
            models.Equipments.objects.exclude(status="3")
            .annotate(month=TruncMonth("created_on"))
            .values("month")
            .annotate(total=Count("id"))
            .values("month", "total")
        )

        return Response({"status": status.HTTP_200_OK, "data": equipment_obj})


class LandingList(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = order_type = order_column = limit_start = limit_end = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = ["name", "description"]
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field]})
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            if pk:
                list = (
                    models.Landingpage.objects.filter(pk=pk).exclude(status="3").get()
                )
                serializeobj = cSerializer.ListLandingpageSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Landingpage.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial type"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.Landingpage.objects.exclude(status="3")
        if normal_values:
            lists = lists.filter(
                reduce(
                    operator.and_,
                    (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
                )
            )
        if array_values:
            for key, values in array_values.items():
                queries = [Q(**{"%s__contains" % key: value}) for value in values]
                query = queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None:
            if order_column:
                lists = lists.order_by(order_column)

        elif order_type in "asc":
            if order_column:
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("id")

        elif order_type in "desc":
            if order_column:
                order_column = "-" + str(order_column)
                lists = lists.order_by(order_column)
            else:
                lists = lists.order_by("-id")

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = cSerializer.ListLandingpageSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class landingCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Landingpage.objects.get(pk=pk)
        except models.Landingpage.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "name" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            if "code" in request.data:
                request.data._mutable = True
                request.data["code"] = (request.data["code"]).upper()
            if "sequence" in request.data:
                request.data["sequence"] = (
                    request.data["sequence"] if (request.data["sequence"] != "") else 0
                )

            if "id" in request.data:
                pk = request.data["id"]
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk or pk == "null":
                    duplicate_code = (
                        models.Landingpage.objects.values("code")
                        .filter(code=request.data["code"])
                        .exclude(status=3)
                    )

                    duplicate_name = (
                        models.Landingpage.objects.values("name")
                        .filter(name=request.data["name"])
                        .exclude(status=3)
                    )

                    if duplicate_code:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit code"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    elif duplicate_name:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit name"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = cSerializer.LandingpageSerializer(
                            data=request.data
                        )
                        if saveserialize.is_valid():
                            saveserialize.save()
                            
                            data_list = json.loads(request.data['satellite_data'])
                            if data_list and saveserialize.data["id"]:
                                for satellite in data_list:
                                    landingmapping = LandingSatMapping.objects.create(
                                        Landing_id =saveserialize.data["id"],
                                        satellite_unit = satellite['satellite_unit'],
                                        url = satellite['url']
                                    )
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New Landing"
                                    + language.context[language.defaultLang]["insert"],
                                    "data": saveserialize.data,
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": error.serializerError(saveserialize),
                                },
                                status=status.HTTP_200_OK,
                            )

                else:
                    if request.data["status"] != 3:
                        duplicate_code = (
                            models.Landingpage.objects.values("code")
                            .filter(code=request.data["code"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        duplicate_name = (
                            models.Landingpage.objects.values("id", "name", "status")
                            .filter(name=request.data["name"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_code:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit code"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                        elif duplicate_name:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit name"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = cSerializer.LandingpageSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        data_list = json.loads(request.data['satellite_data'])
                        if data_list and saveserialize.data["id"]:
                            LandingSatMapping.objects.filter(Landing_id=request.data["id"]).delete()
                            for satellite in data_list:
                                landingmapping = LandingSatMapping.objects.create(
                                    Landing_id =request.data["id"],
                                    satellite_unit = satellite['satellite_unit'],
                                    url = satellite['url']
                                )
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Landing"
                                + language.context[language.defaultLang]["update"],
                                "data": saveserialize.data,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": error.serializerError(saveserialize),
                            },
                            status=status.HTTP_200_OK,
                        )
            else:
                return Response(
                    {
                        "status": {
                            "id": [
                                "id" + language.context[language.defaultLang]["missing"]
                            ]
                        }
                    },
                    status=status.HTTP_200_OK,
                )


class ShipCount(APIView):
    def get(self, request):
        ship_count = (
            models.Ships.objects.values("code")
            .exclude(status="3")
            .annotate(scount=Count("code"))
            .order_by("code")
            .count()
        )
        return Response({"status": status.HTTP_200_OK, "data": ship_count})


class SectionCount(APIView):
    def get(self, request):
        sec_count = (
            models.Sections.objects.values("code")
            .exclude(status="3")
            .annotate(scount=Count("code"))
            .order_by("code")
            .count()
        )
        return Response({"status": status.HTTP_200_OK, "data": sec_count})


class EquipmentCount(APIView):
    def get(self, request):
        eqp_count = (
            models.Equipments.objects.values("code")
            .exclude(status="3")
            .annotate(scount=Count("code"))
            .order_by("code")
            .count()
        )
        # eqp_count=models.Equipments.objects.values('code').distinct().count()
        # print(eqp_count)
        return Response({"status": status.HTTP_200_OK, "data": eqp_count})
