from xmlrpc.client import ResponseError
from django.views.decorators.clickjacking import xframe_options_exempt
from urllib import response
from django.shortcuts import render
from functools import partial
from queue import Empty
from unicodedata import name
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase

# from rest_framework import authentication, AllowAny
# from rest_framework.permissions import Is_Authenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.http import Http404
from functools import reduce
import operator
from django.db.models import Q
from collections import defaultdict
from rest_framework import filters
from configuration.models import Templatestable
import json


from django.db.models import (
    Q,
    F,
    Func,
    Count,
    Avg,
    Case,
    When,
    IntegerField,
    OuterRef,
    Subquery,
    Sum,
)
from django.db import models as dbModels
from django.db.models.expressions import Func as expFunc
from django.db.models.functions import TruncMonth, TruncYear

from NavyTrials import language, error, settings, common
from access.views import Common

from collections import namedtuple

from django.template import Template, Context
from datetime import datetime
import time
from django.template import loader
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa

from django.template import Context, Template
import requests
import json
import barcode
from barcode.writer import ImageWriter
from django.utils.crypto import get_random_string
from . import models
from .serializer import (
    TrialListSerializer,
    TrialSerializer,
    # HSconvertorListSerializer,
    # HSconvertorSerializer,
    # HSconvertorlogSerializer,
    # HSconvertorlogListSerializer,
    trialApprovalSerializer,
    TempImportDataSerializer,
 
)
from master.models import (
    TrialTypes,
    DataAccess,
    DataAccessShip,
    TrialUnits,
    SatelliteUnits,
    Ships,
    Sections,
    Equipments,
    Boilers,
)
from configuration.models import Approval
from notification.models import NotificationUser, NotificationUserLog
from master import models as masterModels
from master.models import Ships
from master import serializer as masterSerializer
from access import models as accessModels
from access import models as accessSerializer

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from os import path
from django.conf import settings
import os
import csv


class TrialsList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = (
            order_type
        ) = order_column = limit_start = limit_end = approved_level = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = None if values == "None" else values

            strings = []
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")
            approved_level = request.GET.get("approved_level")
            count = request.GET.get("count")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")
            if approved_level is not None:
                normal_values.pop("approved_level")
            if count is not None:
                normal_values.pop("count")

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
                list = models.Trials.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = serializer.TrialListSerializer(
                    list, context={"request": request}
                )
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Trials.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial unit"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.Trials.objects.exclude(status="3")
        if "Authorized-Role" in request.headers:
            role_code = request.headers["Authorized-Role"]
            role_id = request.headers["Authorized-By"]
            if role_code != "admin" and (
                role_code != "VIEW"
                or (DataAccess.objects.filter(user_id=request.user.id).count() == 0)
            ):
                satList = DataAccess.objects.values_list(
                    "satellite_unit_id", "trial_unit_id"
                ).filter(user_id=request.user.id)
                shipList = masterModels.DataAccessShip.objects.values_list(
                    "ship_id"
                ).filter(data_access__user_id=request.user.id)
                ship_ids = (o[0] for o in shipList)
                satellite_unit_ids = (o[0] for o in satList)
                trial_unit_ids = (o[1] for o in satList)
                if trial_unit_ids:
                    lists = lists.filter(trial_unit_id__in=trial_unit_ids)
                if satellite_unit_ids:
                    lists = lists.filter(satellite_unit_id__in=satellite_unit_ids)
                if ship_ids:
                    lists = lists.filter(ship_id__in=ship_ids)
                lists = lists.filter(
                    id__in=(
                        models.trialStatus.objects.values("trial_id").filter(
                            process_flow__process_id=request.user.process_id,
                            process_flow__user_role_id=role_id,
                        )
                    )
                )
        lists = lists.order_by("-id")
        if "Authorized-Role" in request.headers:
            role_code = request.headers["Authorized-Role"]
            if role_code != "admin":
                satList = DataAccess.objects.values("satellite_unit_id").filter(
                    user_id=request.user.id
                )
                ids = (o["satellite_unit_id"] for o in satList)
                lists = lists.filter(satellite_unit_id__in=ids)

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

        total_length = lists.count()

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

        if approved_level:
            if approved_level == "-1":
                lists = lists.filter(approved_level=-1)
            elif approved_level == "-2":
                lists = lists.exclude(approved_level=-1)
                role_code = request.headers["Authorized-Role"]
                role_id = int(request.headers["Authorized-By"])
                process_id = int(request.user.process_id)
                if process_id == 2 and role_id == 3:
                    lists = lists.filter(
                        (Q(ship_recommender=2) | Q(ship_recommender=None))
                        & Q(ship_initiater=1)
                    )
                elif process_id == 2 and role_id == 4:
                    lists = lists.filter(
                        (
                            (Q(ship_approver=2) | Q(ship_approver=None))
                            & Q(ship_recommender=1)
                        )
                        | (Q(ship_initiater=1) & Q(ship_recommender=2))
                        | (Q(ship_recommender=None))
                    )
                elif process_id == 2 and role_id == 5:
                    lists = lists.filter(
                        (
                            (Q(trial_initiater=2) | Q(trial_initiater=None))
                            & Q(ship_approver=1)
                        )
                        | (Q(ship_recommender=1) & Q(ship_approver=2))
                        | (Q(ship_approver=None))
                    )
                elif process_id == 3 and role_id == 3:
                    lists = lists.filter(
                        (
                            (Q(trial_recommender=2) | Q(trial_recommender=None))
                            & Q(trial_initiater=1)
                        )
                        | (Q(ship_approver=1) & Q(trial_initiater=2))
                        | (Q(trial_initiater=None))
                    )
                elif process_id == 3 and role_id == 4:
                    lists = lists.filter(
                        (
                            (Q(trial_approver=2) | Q(trial_approver=None))
                            & Q(trial_recommender=1)
                        )
                        | (Q(trial_initiater=1) & Q(trial_recommender=2))
                        | (Q(trial_recommender=None))
                    )
                elif process_id == 3 and role_id == 5:
                    lists = lists.filter(
                        (Q(trial_recommender=1) & Q(trial_approver=None))
                        | (Q(trial_recommender=1) & Q(trial_approver=2))
                    )

            elif approved_level == "-3":
                role_code = request.headers["Authorized-Role"]
                role_id = int(request.headers["Authorized-By"])
                process_id = int(request.user.process_id)
                if process_id == 2 and role_id == 3:
                    # lists = lists.exclude(approved_level=-1)
                    lists = lists.filter(ship_recommender=1, ship_initiater=1)
                elif process_id == 2 and role_id == 4:
                    lists = lists.filter(ship_approver=1, ship_recommender=1)
                elif process_id == 2 and role_id == 5:
                    lists = lists.filter(trial_initiater=1, ship_approver=1)
                elif process_id == 3 and role_id == 3:
                    lists = lists.filter(trial_recommender=1, trial_initiater=1)
                elif process_id == 3 and role_id == 4:
                    lists = lists.filter(trial_approver=1, trial_recommender=1)
                elif process_id == 3 and role_id == 5:
                    lists = lists.filter(trial_approver=1, trial_recommender=1)

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        if count is not None and (count == True or count == "true"):
            return Response(
                {"status": error.context["success_code"], "total_length": total_length},
                status=status.HTTP_200_OK,
            )
        serializer = TrialListSerializer(lists, many=True, context={"request": request})
        return Response(
            {
                "status": error.context["success_code"],
                "data": serializer.data,
                "total_length": total_length,
            },
            status=status.HTTP_200_OK,
        )


class TrialsCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Trials.objects.get(pk=pk)
        except models.Trials.DoesNotExist:
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
        elif "command" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Command"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "satellite_unit" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Satellite unit"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "ship" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Ship"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "section" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Section"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "equipment" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Equipment"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "trial_type" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial type"
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

                if not pk:
                    request.data["created_ip"] = Common.get_client_ip(request)
                    request.data["created_by"] = request.user.id
                    request.data["approved_level"] = 0
                    request.data["ship_initiater"] = 1
                    request.data["legacy_data"] = "No"

                    trialType = (
                        TrialTypes.objects.values("code")
                        .filter(id=request.data["trial_type"])
                        .first()
                    )
                    trial_number = (
                        trialType["code"] if trialType else ""
                    ) + get_random_string(length=8, allowed_chars="1234567890")
                    request.data["trial_number"] = trial_number
                    saveserialize = TrialSerializer(data=request.data)
                    if saveserialize.is_valid():
                        saveserialize.save()
                        trials = TrialListSerializer(
                            models.Trials.objects.filter(id=saveserialize.data["id"]),
                            many=True,
                            context={"request": request},
                        ).data[0]

                        role_id = request.headers["Authorized-By"]
                        models.trialApproval.objects.create(
                            approved_level=1,
                            approved_ip=Common.get_client_ip(request),
                            approved_by_id=request.user.id,
                            trial_id=trials["id"],
                            comments="Initiated",
                            status=1,
                            approved_role_id=role_id,
                            type=-1,
                        )

                        # Status update
                        models.trialStatus.objects.create(
                            trial_id=trials["id"],
                            process_flow_id=1,
                            created_by_id=request.user.id,
                            created_ip=Common.get_client_ip(request),
                        )
                        models.trialStatus.objects.create(
                            trial_id=trials["id"],
                            process_flow_id=2,
                            created_by_id=request.user.id,
                            created_ip=Common.get_client_ip(request),
                        )

                        # Notification functionality

                        notificationMessage = (
                            "New "
                            + (trials["trial_type"]["type"]).lower()
                            + " request ("
                            + trials["trial_number"]
                            + ") has been initiated by "
                            + (
                                trials["created_by"]["first_name"]
                                + " "
                                + trials["created_by"]["last_name"]
                            )
                        )
                        # intiate not create the noitification
                        # NotificationUser.objects.create(
                        #     trial_unit_id=request.data["trial_unit"],
                        #     satellite_unit_id=request.data["satellite_unit"],
                        #     trial_id=saveserialize.data["id"],
                        #     message=notificationMessage,
                        # )

                        # First level approval notification
                        # firstApproval=Approval.objects.values().filter(level=1,trail_unit_id=request.data['trial_unit'],satellite_unit_id=request.data['satellite_unit']).first()
                        firstApproval = (
                            accessModels.ProcessFlow.objects.values()
                            .filter(level=2)
                            .first()
                        )

                        if firstApproval:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " request ("
                                + trials["trial_number"]
                                + ") is waiting for your recommendation "
                            )
                            NotificationUser.objects.create(
                                trial_unit_id=request.data["trial_unit"],
                                satellite_unit_id=request.data["satellite_unit"],
                                trial_id=saveserialize.data["id"],
                                message=notificationMessage,
                                user_role_id=firstApproval["user_role_id"],
                                process_id=firstApproval["process_id"],
                            )

                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": (trials["trial_type"]["type"])
                                + language.context[language.defaultLang]["initiated"],
                                "data": trials,
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
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id
                    list = self.get_object(pk)
                    saveserialize = TrialSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        saveserialize.save()
                        trials = TrialListSerializer(
                            models.Trials.objects.filter(id=saveserialize.data["id"]),
                            many=True,
                            context={"request": request},
                        ).data[0]
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Trial"
                                + language.context[language.defaultLang]["update"],
                                "data": trials,
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


class TrialsApprovalList(APIView):
    def get(self, request, pk=None):
        filter_values = dict(request.GET.items())
        search_string = (
            order_type
        ) = order_column = limit_start = limit_end = approved_level = ""
        normal_values = dict()
        array_values = dict()
        if filter_values:
            for key, values in filter_values.items():
                if values.find("[") != -1 and values.find("]") != -1:
                    res = values.strip("][").split(",")
                    array_values[key] = res
                else:
                    normal_values[key] = values

            strings = []
            search_string = dict(
                (k, normal_values[k]) for k in strings if k in normal_values
            )
            order_column = request.GET.get("order_column")
            order_type = request.GET.get("order_type")
            limit_start = request.GET.get("limit_start")
            limit_end = request.GET.get("limit_end")
            approved_level = request.GET.get("approved_level")

            if order_column is not None:
                normal_values.pop("order_column")
            if order_type is not None:
                normal_values.pop("order_type")
            if limit_start is not None:
                normal_values.pop("limit_start")
            if limit_end is not None:
                normal_values.pop("limit_end")
            if approved_level is not None:
                normal_values.pop("approved_level")

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
                    models.trialApproval.objects.filter(pk=pk).exclude(status="3").get()
                )
                serializeobj = serializer.trialApprovalSerializer(
                    list, context={"request": request}
                )
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.trialApproval.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial unit"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        # lists = models.trialApproval.objects.exclude(status='3')

        lists = lists.order_by("id")

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

        if approved_level:
            if approved_level == "-1":
                lists = lists.filter(approved_level=-1)
            elif approved_level == "-2":
                lists = lists.exclude(approved_level=-1)

        if limit_start and limit_end:
            lists = lists[int(limit_start) : int(limit_end)]

        elif limit_start:
            lists = lists[int(limit_start) :]

        elif limit_end:
            lists = lists[0 : int(limit_end)]

        serializer = trialApprovalSerializer(
            lists, many=True, context={"request": request}
        )
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


# initiate to Rec Fuction
class IntiateToRec(APIView):
    def get_object(self, pk):
        try:
            return models.Trials.objects.get(pk=pk)
        except models.Trials.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        print("hlo", request.data)
        trial_type = request.data["trial_type__type"]
        notificationMessage = (
            "New "
            + (trial_type).lower()
            + " request ("
            + request.data["trial_number"]
            + ") has been initiated by "
            + (request.data["first_name"] + " " + request.data["last_name"])
            + "  and waiting for your recommendation"
        )
        print("Notify", notificationMessage)
        # intiate not create the noitification
        NotificationUser.objects.create(
            trial_unit_id=request.data["trial_unit_id"],
            satellite_unit_id=request.data["satellite_unit_id"],
            trial_id=request.data["id"],
            message=notificationMessage,
        )
        trials = models.Trials.objects.filter(id=request.data["id"]).update(
            approved_level=request.data["approval_level"]
        )
        return Response(
            {
                "status": error.context["success_code"],
                "message": trial_type + " form sent to recommendation successfully.",
                "data": trials,
            },
            status=status.HTTP_200_OK,
        )

# TrialsApproval
class TrialsApproval(APIView):
    def post(self, request, pk=None):
        notificationMessage = "."
        if "approved_level" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Level"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "trial_id" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial ID"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "comments" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Comment"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "status" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Status"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "approved_role_id" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Approved Role ID"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            try:
                if int(request.data["approved_level"]) == 2:
                    models.Trials.objects.filter(id=request.data["trial_id"]).update(
                        ship_recommender=request.data["status"]
                    )
                elif int(request.data["approved_level"]) == 3:
                    models.Trials.objects.filter(id=request.data["trial_id"]).update(
                        ship_approver=request.data["status"]
                    )
                elif int(request.data["approved_level"]) == 4:
                    models.Trials.objects.filter(id=request.data["trial_id"]).update(
                        trial_initiater=request.data["status"]
                    )
                elif int(request.data["approved_level"]) == 5:
                    models.Trials.objects.filter(id=request.data["trial_id"]).update(
                        trial_recommender=request.data["status"]
                    )
                elif int(request.data["approved_level"]) == 6:
                    models.Trials.objects.filter(id=request.data["trial_id"]).update(
                        trial_approver=request.data["status"]
                    )
                if request.data["status"] == 1:
                    approvalData = (
                        accessModels.ProcessFlow.objects.values()
                        .filter(level__gt=int(request.data["approved_level"]))
                        .order_by("id")
                        .first()
                    )
                    if approvalData:
                        # Next level approval notification
                        trials = TrialListSerializer(
                            models.Trials.objects.filter(id=request.data["trial_id"]),
                            many=True,
                            context={"request": request},
                        ).data[0]

                        models.trialStatus.objects.create(
                            trial_id=trials["id"],
                            process_flow_id=approvalData["id"],
                            created_by_id=request.user.id,
                            created_ip=Common.get_client_ip(request),
                        )

                        if approvalData["level"] == 2:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " request ("
                                + trials["trial_number"]
                                + ") is re initiated again and waiting for your approval "
                            )
                        elif approvalData["level"] == 3:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " request ("
                                + trials["trial_number"]
                                + ") is waiting for your approval "
                            )
                        elif approvalData["level"] == 4:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " requestion ("
                                + trials["trial_number"]
                                + ") is approved and waiting for you to submit"
                            )
                        elif approvalData["level"] == 5:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " ("
                                + trials["trial_number"]
                                + ") has submitted and waiting for your recommendation"
                            )
                        elif approvalData["level"] == 6:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " ("
                                + trials["trial_number"]
                                + ") has recommended for your approval"
                            )

                        NotificationUser.objects.create(
                            trial_unit_id=trials["trial_unit"]["id"],
                            satellite_unit_id=trials["satellite_unit"]["id"],
                            trial_id=trials["id"],
                            message=notificationMessage,
                            user_role_id=approvalData["user_role_id"],
                            process_id=approvalData["process_id"],
                        )

                        models.Trials.objects.filter(
                            id=request.data["trial_id"]
                        ).update(approved_level=approvalData["level"])
                    else:
                        # Approved notification
                        trials = TrialListSerializer(
                            models.Trials.objects.filter(id=request.data["trial_id"]),
                            many=True,
                            context={"request": request},
                        ).data[0]

                        notificationMessage = (
                            (trials["trial_type"]["type"])
                            + "  ("
                            + trials["trial_number"]
                            + ") has been approved and report has been generated"
                        )
                        NotificationUser.objects.create(
                            trial_unit_id=trials["trial_unit"]["id"],
                            satellite_unit_id=trials["satellite_unit"]["id"],
                            trial_id=trials["id"],
                            message=notificationMessage,
                        )

                        models.Trials.objects.filter(
                            id=request.data["trial_id"]
                        ).update(approved_level="-1")

                    # models.trialApproval.objects.filter(approved_by_id=request.user.id,trial_id=request.data['trial_id'],approved_role_id=request.data['approved_role_id']).delete()
                    models.trialApproval.objects.create(
                        approved_level=request.data["approved_level"],
                        approved_ip=Common.get_client_ip(request),
                        approved_by_id=request.user.id,
                        trial_id=request.data["trial_id"],
                        comments=request.data["comments"],
                        status=request.data["status"],
                        approved_role_id=request.data["approved_role_id"],
                        type=request.data["type"],
                    )
                    return Response(
                        {
                            "status": error.context["success_code"],
                            "message": "Recommendation updated successfully",
                        },
                        status=status.HTTP_200_OK,
                    )
                elif request.data["status"] == 2:
                    approvalData = (
                        accessModels.ProcessFlow.objects.values()
                        .filter(level__lt=int(request.data["approved_level"]))
                        .order_by("-id")
                        .first()
                    )
                    if approvalData:
                        trials = TrialListSerializer(
                            models.Trials.objects.filter(id=request.data["trial_id"]),
                            many=True,
                            context={"request": request},
                        ).data[0]

                        # Previous level approval notification
                        if approvalData["level"] == 1 or approvalData["level"] == 4:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " request ("
                                + trials["trial_number"]
                                + ") is returned from recommender "
                            )
                        elif approvalData["level"] == 2 or approvalData["level"] == 5:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " requestion ("
                                + trials["trial_number"]
                                + ") is returned from approver"
                            )
                        elif approvalData["level"] == 3:
                            notificationMessage = (
                                (trials["trial_type"]["type"])
                                + " requestion ("
                                + trials["trial_number"]
                                + ") is returned from initiater of trial unit"
                            )

                        NotificationUser.objects.create(
                            trial_unit_id=trials["trial_unit"]["id"],
                            satellite_unit_id=trials["satellite_unit"]["id"],
                            trial_id=trials["id"],
                            message=notificationMessage,
                            user_role_id=approvalData["user_role_id"],
                            process_id=approvalData["process_id"],
                        )

                        models.trialStatus.objects.create(
                            trial_id=trials["id"],
                            process_flow_id=approvalData["id"],
                            created_by_id=request.user.id,
                            created_ip=Common.get_client_ip(request),
                        )

                        models.trialApproval.objects.create(
                            approved_level=request.data["approved_level"],
                            approved_ip=Common.get_client_ip(request),
                            approved_by_id=request.user.id,
                            trial_id=request.data["trial_id"],
                            comments=request.data["comments"],
                            status=request.data["status"],
                            approved_role_id=request.data["approved_role_id"],
                            type=request.data["type"],
                        )

                        models.Trials.objects.filter(
                            id=request.data["trial_id"]
                        ).update(approved_level=approvalData["level"])

                    return Response(
                        {
                            "status": error.context["success_code"],
                            "message": "Returned back to previous level successfully",
                        },
                        status=status.HTTP_200_OK,
                    )

            except:
                return Response(
                    {
                        "status": error.context["error_code"],
                        "message": "Failed to perform this action",
                    },
                    status=status.HTTP_200_OK,
                )

class ApprovalHistory(APIView):
    def post(self, request, pk=None):
        if "trial_id" in request.data:
            history = (
                models.trialApproval.objects.values(
                    "id",
                    "status",
                    "comments",
                    "approved_on",
                    "approved_by__first_name",
                    "approved_by__last_name",
                    "approved_by__process__name",
                    "approved_role__name",
                )
                .filter(trial_id=request.data["trial_id"])
                .order_by("id")
            )
            return Response(
                {"status": error.context["success_code"], "data": history},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": error.context["success_code"], "data": "No data"},
                status=status.HTTP_200_OK,
            )


# ........................
# class TrialImport(APIView)
#     def post(self,request, pk = None):
#         request_file = request.FILES['file_upload']
#         dir_storage='static/import_excel'
#         fs = FileSystemStorage(location=dir_storage)
#         filename = fs.save(request_file.name, request_file)
#         if os.path.splitext(request_file.name)[1] == ".xls" or  os.path.splitext(request_file.name)[1] == ".xlsx":
#             excel_folder = os.path.join(settings.BASE_DIR, 'static/import_excel/')
#             read_file = pd.read_excel(request_file)
#             read_file.to_csv(excel_folder +'import_excel_file.csv')
#             fhand = open('static/import_excel/import_excel_file.csv')
#         else:
#              return Response({"status":error.context['error_code'],"message" : "File format not supported (Xls and Xlsx only allowed)" })
#         reader = csv.reader(fhand)
#         next(reader)
#         request_data = dict()
#         for row in reader:

#             if not row[1]:
#                 return Response({"status":error.context['error_code'],"message" : "Trial Code is required" })
#             if not row[2]:
#                 return Response({"status":error.context['error_code'],"message" : "Satellite unit Code is required" })
#             if not row[3]:
#                 return Response({"status":error.context['error_code'],"message" : "Ship Code is required" })
#             if not row[4]:
#                 return Response({"status":error.context['error_code'],"message" : "Section Code is required" })
#             if not row[7]:
#                 return Response({"status":error.context['error_code'],"message" : "Trial type Code is required" })

#             if row[1]:
#                 if row[1]=="CBIU":
#                     trial = TrialUnits.objects.filter(code=row[1]).first()

#                     sat = SatelliteUnits.objects.filter(code=row[2]).first()

#                     ship = Ships.objects.filter(code=row[3], trial_unit_id=trial.id).first()

#                     section = Sections.objects.filter(code=row[4], trial_unit_id=trial.id, satellite_unit_id=sat.id, ship_id=ship.id).first()

#                     boiler = Boilers.objects.filter(code=row[6], trial_unit_id=trial.id, satellite_unit_id=sat.id, ship_id=ship.id, section_id=section.id).first()

#                     trial_type = TrialTypes.objects.filter(code=row[7],trial_unit_id=trial.id).first()


#                     request_data = {
#                     "trial_unit":trial.id,
#                     "satellite_unit":sat.id,
#                     "ship":ship.id,
#                     "section":section.id,
#                     # "eqp":eqp.id,
#                     "boiler":boiler.id,
#                     "trial_type":trial_type.id,
#                     "trial_date":row[8]
#                     }

#                     sobj = TempImportDataSerializer(data= request_data)
#                     if sobj.is_valid():

#                         ltc = models.TempImportData(trial_unit=trial.id,
#                                                 satellite_unit=sat.id,
#                                                 ship=ship.id,
#                                                 section=section.id,
#                                                 # eqp=eqp.id,
#                                                 boilers=boiler.id,
#                                                 trial_type= trial_type.id,
#                                                 trial_date=row[8]
#                                                 )
#                         ltc.save()

#                 else:
#                     trial = TrialUnits.objects.filter(code=row[1]).first()

#                     sat = SatelliteUnits.objects.filter(code=row[2]).first()

#                     ship = Ships.objects.filter(code=row[3], trial_unit_id=trial.id).first()

#                     section = Sections.objects.filter(code=row[4], trial_unit_id=trial.id, satellite_unit_id=sat.id, ship_id=ship.id).first()

#                     eqp = Equipments.objects.filter(code=row[5], trial_unit_id=trial.id, satellite_unit_id=sat.id, ship_id=ship.id, section_id=section.id).first()

#                     trial_type = TrialTypes.objects.filter(code=row[7],trial_unit_id=trial.id).first()

#                     request_data = {
#                             "trial_unit":trial.id,
#                             "satellite_unit":sat.id,
#                             "ship":ship.id,
#                             "section":section.id,
#                             "eqp":eqp.id,
#                             "trial_type":trial_type.id,
#                             # "boiler":boiler.id,
#                             "trial_date":row[8]
#                         }

#                     sobj = TempImportDataSerializer(data= request_data)
#                     if sobj.is_valid():

#                         ltc = models.TempImportData(trial_unit=trial.id,
#                                                     satellite_unit=sat.id,
#                                                     ship=ship.id,
#                                                     section=section.id,
#                                                     equipment=eqp.id,
#                                                     # boiler=boiler.id,
#                                                     trial_type= trial_type.id,
#                                                     trial_date=row[8]
#                                                     )
#                         ltc.save()
#                         temp_id = models.TempImportData.objects.values_list('id','trial_unit','satellite_unit','ship','equipment','boilers','section','trial_type','trial_date')

#                         for val in temp_id:
#                             created_ip  = Common.get_client_ip(request)
#                             created_by  = request.user.id
#                             approved_level  = 2
#                             ship_initiater  = 1
#                             status  = 1

#                             trialType=TrialTypes.objects.values('code').filter(id=val[7]).first()
#                             trial_number=(trialType['code'] if trialType else '')+get_random_string(length=8, allowed_chars='1234567890')

#                             create_data = models.Trials.objects.create(trial_unit_id=val[1],satellite_unit_id=val[2],ship_id=val[3],equipment_id=val[4],boilers_id=val[5],section_id=val[6],trial_type_id=val[7],trial_number=trial_number,created_ip=created_ip,created_by_id=created_by,approved_level=approved_level,ship_initiater=ship_initiater,status=status,created_on=val[8])

#                             del_temp=models.TempImportData.objects.all().delete()

#         return Response({"status":error.context['success_code'],"message" : "File imported successfully"})


# ........................................


# 1
# class HSConverterList(APIView):
#     def get(self, request, pk=None):
#         filter_values = dict(request.GET.items())
#         search_string = order_type = order_column = limit_start = limit_end = ""
#         normal_values = dict()
#         array_values = dict()
#         if filter_values:
#             for key, values in filter_values.items():
#                 if values.find("[") != -1 and values.find("]") != -1:
#                     res = values.strip("][").split(",")
#                     array_values[key] = res
#                 else:
#                     normal_values[key] = values

#             strings = []
#             search_string = dict(
#                 (k, normal_values[k]) for k in strings if k in normal_values
#             )
#             order_column = request.GET.get("order_column")
#             order_type = request.GET.get("order_type")
#             limit_start = request.GET.get("limit_start")
#             limit_end = request.GET.get("limit_end")

#             if order_column is not None:
#                 normal_values.pop("order_column")
#             if order_type is not None:
#                 normal_values.pop("order_type")
#             if limit_start is not None:
#                 normal_values.pop("limit_start")
#             if limit_end is not None:
#                 normal_values.pop("limit_end")

#             for key in strings:
#                 if key in normal_values:
#                     normal_values.pop(key)

#             if search_string:
#                 filter_string = None
#                 for field in search_string:
#                     q = Q(**{"%s__contains" % field: search_string[field]})
#                     if filter_string:
#                         filter_string = filter_string & q
#                     else:
#                         filter_string = q
#         try:
#             if pk:
#                 list = (
#                     models.HSconvertor.objects.filter(pk=pk).exclude(status="3").get()
#                 )
#                 serializeobj = serializer.HSconvertorListSerializer(list)
#                 return Response(
#                     {
#                         "status": error.context["success_code"],
#                         "data": serializeobj.data,
#                     },
#                     status=status.HTTP_200_OK,
#                 )

#         except models.HSconvertor.DoesNotExist:
#             return Response(
#                 {
#                     "status": error.context["error_code"],
#                     "message": "Trial unit"
#                     + language.context[language.defaultLang]["dataNotFound"],
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         lists = models.HSconvertor.objects
#         if normal_values:
#             lists = lists.filter(
#                 reduce(
#                     operator.and_,
#                     (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
#                 )
#             )
#         if array_values:
#             for key, values in array_values.items():
#                 queries = [Q(**{"%s__contains" % key: value}) for value in values]
#                 query = queries.pop()
#                 for item in queries:
#                     query |= item
#                 lists = lists.filter(query)

#         if search_string:
#             lists = lists.filter(filter_string)

#         if order_type is None:
#             if order_column:
#                 lists = lists.order_by(order_column)

#         elif order_type in "asc":
#             if order_column:
#                 lists = lists.order_by(order_column)
#             else:
#                 lists = lists.order_by("id")

#         elif order_type in "desc":
#             if order_column:
#                 order_column = "-" + str(order_column)
#                 lists = lists.order_by(order_column)
#             else:
#                 lists = lists.order_by("-id")

#         if limit_start and limit_end:
#             lists = lists[int(limit_start) : int(limit_end)]

#         elif limit_start:
#             lists = lists[int(limit_start) :]

#         elif limit_end:
#             lists = lists[0 : int(limit_end)]

#         serializer = HSconvertorListSerializer(lists, many=True)
#         return Response(
#             {"status": error.context["success_code"], "data": serializer.data},
#             status=status.HTTP_200_OK,
#         )



# class HSConverterCRUD(APIView):
#     def get_object(self, pk):
#         try:
#             return models.HSconvertor.objects.get(pk=pk)
#         except models.HSconvertor.DoesNotExist:
#             raise Http404

#     def post(self, request, pk=None):
#         if "id" not in request.data:
#             return Response(
#                 {
#                     "status": {
#                         "id": ["id" + language.context[language.defaultLang]["missing"]]
#                     }
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             pk = request.data["id"]
#             if not request.data["trial"]:
#                 return Response(
#                     {
#                         "status": error.context["error_code"],
#                         "message": "Trial details are missing",
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             if not pk:
#                 saveserialize = HSconvertorSerializer(data=request.data)

#                 if saveserialize.is_valid():
#                     models.HSconvertor.objects.filter(
#                         trial_id=request.data["trial"]
#                     ).delete()
#                     saveserialize.save()
#                     logData = request.data
#                     logData["running_id"] = saveserialize.data["id"]
#                     saveserializelog = HSconvertorlogSerializer(data=logData)
#                     if saveserializelog.is_valid():
#                         saveserializelog.save()
#                     trials = HSconvertorListSerializer(
#                         models.HSconvertor.objects.filter(id=saveserialize.data["id"]),
#                         many=True,
#                     ).data[0]
#                     return Response(
#                         {
#                             "status": error.context["success_code"],
#                             "message": "New HS Converter trial"
#                             + language.context[language.defaultLang]["insert"],
#                             "data": trials,
#                         },
#                         status=status.HTTP_200_OK,
#                     )
#                 else:
#                     return Response(
#                         {
#                             "status": error.context["error_code"],
#                             "message": error.serializerError(saveserialize),
#                         },
#                         status=status.HTTP_200_OK,
#                     )
#             else:
#                 request.data["modified_ip"] = Common.get_client_ip(request)
#                 request.data["modified_by"] = request.user.id
#                 list = self.get_object(pk)
#                 saveserialize = HSconvertorSerializer(
#                     list, data=request.data, partial=True
#                 )
#                 if saveserialize.is_valid():
#                     saveserialize.save()
#                     logData = request.data
#                     logData["running_id"] = saveserialize.data["id"]
#                     saveserializelog = HSconvertorlogSerializer(data=logData)
#                     if saveserializelog.is_valid():
#                         saveserializelog.save()
#                     trials = HSconvertorListSerializer(
#                         models.HSconvertor.objects.filter(id=saveserialize.data["id"]),
#                         many=True,
#                     ).data[0]
#                     return Response(
#                         {
#                             "status": error.context["success_code"],
#                             "message": "HS Converter trial"
#                             + language.context[language.defaultLang]["update"],
#                             "data": trials,
#                         },
#                         status=status.HTTP_200_OK,
#                     )
#                 else:
#                     return Response(
#                         {
#                             "status": error.context["error_code"],
#                             "message": error.serializerError(saveserialize),
#                         },
#                         status=status.HTTP_200_OK,
#                     )


# class HSConverterlogList(APIView):
#     def get(self, request, pk=None):
#         filter_values = dict(request.GET.items())
#         search_string = order_type = order_column = limit_start = limit_end = ""
#         normal_values = dict()
#         array_values = dict()
#         if filter_values:
#             for key, values in filter_values.items():
#                 if values.find("[") != -1 and values.find("]") != -1:
#                     res = values.strip("][").split(",")
#                     array_values[key] = res
#                 else:
#                     normal_values[key] = values

#             strings = []
#             search_string = dict(
#                 (k, normal_values[k]) for k in strings if k in normal_values
#             )
#             order_column = request.GET.get("order_column")
#             order_type = request.GET.get("order_type")
#             limit_start = request.GET.get("limit_start")
#             limit_end = request.GET.get("limit_end")

#             if order_column is not None:
#                 normal_values.pop("order_column")
#             if order_type is not None:
#                 normal_values.pop("order_type")
#             if limit_start is not None:
#                 normal_values.pop("limit_start")
#             if limit_end is not None:
#                 normal_values.pop("limit_end")

#             for key in strings:
#                 if key in normal_values:
#                     normal_values.pop(key)

#             if search_string:
#                 filter_string = None
#                 for field in search_string:
#                     q = Q(**{"%s__contains" % field: search_string[field]})
#                     if filter_string:
#                         filter_string = filter_string & q
#                     else:
#                         filter_string = q
#         try:
#             if pk:
#                 list = (
#                     models.HSconvertorlog.objects.filter(pk=pk)
#                     .exclude(status="3")
#                     .get()
#                 )
#                 serializeobj = serializer.HSconvertorlogListSerializer(list)
#                 return Response(
#                     {
#                         "status": error.context["success_code"],
#                         "data": serializeobj.data,
#                     },
#                     status=status.HTTP_200_OK,
#                 )

#         except models.HSconvertorlog.DoesNotExist:
#             return Response(
#                 {
#                     "status": error.context["error_code"],
#                     "message": "Trial unit"
#                     + language.context[language.defaultLang]["dataNotFound"],
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         lists = models.HSconvertorlog.objects
#         if normal_values:
#             lists = lists.filter(
#                 reduce(
#                     operator.and_,
#                     (Q(**d) for d in [dict([i]) for i in normal_values.items()]),
#                 )
#             )
#         if array_values:
#             for key, values in array_values.items():
#                 queries = [Q(**{"%s__contains" % key: value}) for value in values]
#                 query = queries.pop()
#                 for item in queries:
#                     query |= item
#                 lists = lists.filter(query)

#         if search_string:
#             lists = lists.filter(filter_string)

#         if order_type is None:
#             if order_column:
#                 lists = lists.order_by(order_column)

#         elif order_type in "asc":
#             if order_column:
#                 lists = lists.order_by(order_column)
#             else:
#                 lists = lists.order_by("id")

#         elif order_type in "desc":
#             if order_column:
#                 order_column = "-" + str(order_column)
#                 lists = lists.order_by(order_column)
#             else:
#                 lists = lists.order_by("-id")

#         if limit_start and limit_end:
#             lists = lists[int(limit_start) : int(limit_end)]

#         elif limit_start:
#             lists = lists[int(limit_start) :]

#         elif limit_end:
#             lists = lists[0 : int(limit_end)]

#         serializer = HSconvertorlogListSerializer(lists, many=True)
#         return Response(
#             {"status": error.context["success_code"], "data": serializer.data},
#             status=status.HTTP_200_OK,
#         )



from django import template
from django.utils import formats
import datetime

register = template.Library()


@register.filter(expects_localtime=True, is_safe=False)
def custom_date(value, arg=None):
    if value in (None, ""):
        return ""

    if isinstance(value, str):
        api_date_format = "%Y-%m-%dT%H:%M:%S.%f%z"  # 2019-08-30T08:22:32.245-0700
        value = datetime.datetime.strptime(value, api_date_format)

    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ""


@xframe_options_exempt
def hs_converter(self, trial_id=None):
    users = models.HSconvertor.objects.values().filter(trial_id=trial_id).first()
    approvalHistory = trialApprovalSerializer(
        models.trialApproval.objects.filter(trial_id=trial_id), many=True
    ).data
    context = {"users": users, "approvalData": approvalHistory, "self": self}

    html = loader.render_to_string("service/hs-converter.html", context=context)
    import pdfkit
    import platform

    if platform.system() == "Windows":
        pdf = pdfkit.from_string(
            html,
            False,
            verbose=True,
            configuration=pdfkit.configuration(wkhtmltopdf=common.WKHTML_PATH),
        )
    else:
        pdf = pdfkit.from_string(html, False, verbose=True)
    response = HttpResponse(pdf, content_type="application/pdf")
    if response:
        return response  # returns the response.

    return HttpResponse(html, content_type="text/html")



