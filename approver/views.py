# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from NavyTrials import language,error,settings,common
# from access.views import Common
# from . import models


from django.views.decorators.clickjacking import xframe_options_exempt
from urllib import response
from django.shortcuts import render
from functools import partial
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
from collections import defaultdict
from rest_framework import filters
from configuration.models import Templatestable


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

# from . import serializer
# from . import serializer as cSerializer
from configuration.models import Approval
from notification.models import NotificationUser, NotificationUserLog

# from master import models as masterModels
from master import serializer as masterSerializer
from access import models as accessModels

# from accounts import models as accountsModels

from notification import models as notificationModels
from access import models as accessSerializer

# import pandas as pd
import uuid
import os
import csv
from django.core.files.storage import FileSystemStorage

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django.http import JsonResponse
from django.template.loader import render_to_string


class ConfigCRUD(APIView):
    authentication_classes = []  # disables authentication
    permission_classes = []  # disables permission

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
        else:
            # print(request.data,"adad")
            if request.data["id"] == None:
                # print(request.data['name'],"adad2222")
                models.Config.objects.create(
                    name=request.data["name"],
                    code=request.data["code"],
                    desc=request.data["desc"],
                    created_by_id=request.user.id,
                    created_ip=Common.get_client_ip(request),
                    status=request.data["status"],
                )
                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": "Config created successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                if request.data["status"] != 3:
                    models.Config.objects.filter(id=request.data["id"]).update(
                        name=request.data["name"],
                        code=request.data["code"],
                        desc=request.data["desc"],
                        modified_by_id=request.user.id,
                        modified_ip=Common.get_client_ip(request),
                        status=request.data["status"],
                    )

                    return Response(
                        {
                            "status": error.context["success_code"],
                            "message": "Config updated successfully",
                        },
                        status=status.HTTP_200_OK,
                    )

                else:
                    models.Config.objects.filter(id=request.data["id"]).update(
                        status=request.data["status"]
                    )

                    return Response(
                        {
                            "status": error.context["success_code"],
                            "message": "Config deleted successfully",
                        },
                        status=status.HTTP_200_OK,
                    )


class ConfigList(APIView):
    def get(self, request, pk=None):
        config = (
            models.Config.objects.values("id", "name", "code", "desc", "status")
            .exclude(status=3)
            .order_by("-id")
        )
        return Response(
            {"status": error.context["success_code"], "data": config},
            status=status.HTTP_200_OK,
        )


class ApprovedConfigCRUD(APIView):
    def post(self, request, pk=None):
        if "config_id" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Config Id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "role_id" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Role Id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        if "user_id" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User Id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "type" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Type"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "level" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Level"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            # print(request.data,"adad")
            if request.data["id"] == None:
                # print(request.data['name'],"adad2222")
                models.ApprovedConfig.objects.create(
                    config_id=request.data["config_id"],
                    role_id=request.data["role_id"],
                    user_id=request.data["user_id"],
                    type=request.data["type"],
                    level=request.data["level"],
                    created_by_id=request.user.id,
                    created_ip=Common.get_client_ip(request),
                    status=request.data["status"],
                )
                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": "Approved config created successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                if request.data["status"] != 3:
                    models.ApprovedConfig.objects.filter(id=request.data["id"]).update(
                        config_id=request.data["config_id"],
                        role_id=request.data["role_id"],
                        user_id=request.data["user_id"],
                        type=request.data["type"],
                        level=request.data["level"],
                        modified_by_id=request.user.id,
                        modified_ip=Common.get_client_ip(request),
                        status=request.data["status"],
                    )

                    return Response(
                        {
                            "status": error.context["success_code"],
                            "message": "Approved config updated successfully",
                        },
                        status=status.HTTP_200_OK,
                    )

                else:
                    models.ApprovedConfig.objects.filter(id=request.data["id"]).update(
                        status=request.data["status"]
                    )

                    return Response(
                        {
                            "status": error.context["success_code"],
                            "message": "Approved config deleted successfully",
                        },
                        status=status.HTTP_200_OK,
                    )


class ApprovedConfigList(APIView):
    def get(self, request, pk=None):
        res = (
            models.ApprovedConfig.objects.values(
                "id",
                "config_id",
                "config_id__name",
                "role_id",
                "role_id__name",
                "user_id",
                "user_id__first_name",
                "user_id__last_name",
                "type",
                "level",
                "status",
            )
            .exclude(status=3)
            .order_by("-id")
        )
        return Response(
            {"status": error.context["success_code"], "data": res},
            status=status.HTTP_200_OK,
        )


# Check Approved Config Id.
class GetApprovedDetails(APIView):
    authentication_classes = []  # disables authentication
    permission_classes = []  # disables permission

    def get(self, request, pk=None):
        if "role_id" not in request.GET:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Role Id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "user_id" not in request.GET:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User Id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )

        else:
            user_id = request.GET["user_id"]
            role_id = request.GET["role_id"]

            # Check with approved config.
            ac_res = (
                models.ApprovedConfig.objects.values(
                    "id", "role_id", "user_id", "type", "level"
                )
                .filter(role_id=role_id, user_id=user_id)
                .first()
            )

            if ac_res:
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": ac_res,
                        "message": "Data found",
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": "No data found",
                    },
                    status=status.HTTP_200_OK,
                )


class ApprovalStatusList(APIView):
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
                    models.ApprovalStatus.objects.filter(pk=pk)
                    .exclude(status="3")
                    .get()
                )
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": list,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.ApprovalStatus.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Section"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )
        lists = models.ApprovalStatus.objects.values(
            "id",
            "transaction_id",
            "notes",
            "created_on",
            "final_approval",
            "approved_config_id",
            "created_by_id",
            "modified_by_id",
            "status",
        ).exclude(status=3)
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
        return Response(
            {
                "status": error.context["success_code"],
                "data": lists,
            },
            status=status.HTTP_200_OK,
        )


class ApprovalStatus(APIView):
    authentication_classes = []  # disables authentication
    permission_classes = []  # disables permission

    def post(self, request, pk=None):
        if "trans_id" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Transaction Id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "role_id" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Role Id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        if "user_id" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User Id"
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
        else:
            trans_id = request.data["trans_id"]
            # config_id = request.data["config_id"]
            user_id = request.data["user_id"]
            role_id = request.data["role_id"]
            status = request.data["status"]  # Accept / Rejected
            notes = request.data["notes"]
            # Check with approved config.
            ac_res = (
                models.ApprovedConfig.objects.values(
                    "id", "config_id", "role_id", "user_id", "type", "level"
                )
                .filter(role_id=role_id, user_id=user_id)
                .first()
            )
            if ac_res:
                if ac_res["type"] == 2:
                    ac_count = models.ApprovedConfig.objects.filter(type=2).count()
                else:
                    ac_count = None

                as_count = models.ApprovalStatus.objects.filter(
                    transaction_id=trans_id
                ).count()

                if as_count > 0:
                    update = models.ApprovalStatus.objects.filter(
                        transaction_id=trans_id
                    ).update(
                        transaction_id=trans_id,
                        approved_config_id=ac_res["id"],
                        notes=notes,
                        status=status,
                        final_approval=1
                        if ac_count == ac_res["level"] and status == "1"
                        else None,
                        # modified_by_id = request.user.id,
                        modified_by_id=user_id,
                        modified_ip=Common.get_client_ip(request),
                    )

                else:
                    ins = models.ApprovalStatus.objects.create(
                        transaction_id=trans_id,
                        approved_config_id=ac_res["id"],
                        notes=notes,
                        status=status,
                        created_by_id=user_id,
                        final_approval=1
                        if ac_count == ac_res["level"] and status == "1"
                        else None,
                        # modified_by_id = request.user.id,
                        modified_by_id=user_id,
                        modified_ip=Common.get_client_ip(request),
                    )

                log = models.ApprovalHistory.objects.create(
                    transaction_id=trans_id,
                    approved_config_id=ac_res["id"],
                    notes=notes,
                    status=status,
                    created_by_id=user_id,
                    modified_by_id=user_id,
                    modified_ip=Common.get_client_ip(request),
                )

                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": "Approved config created successfully",
                    }
                )

            else:
                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": "Approval status not created",
                    }
                )


class ApprovalHistory(APIView):
    def post(self, request, pk=None):
        trans_id = request.data["trans_id"]
        lists = (
            models.ApprovalHistory.objects.values(
                "id",
                "transaction_id",
                "notes",
                "created_on",
                "approved_config_id",
                "created_by_id",
                "modified_by_id",
                "status",
            )
            .filter(transaction_id=trans_id)
            .exclude(status=3)
        )
        return Response(
            {
                "status": error.context["success_code"],
                "data": lists,
            },
            status=status.HTTP_200_OK,
        )
