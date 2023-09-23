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
#from rest_framework import authentication, AllowAny
#from rest_framework.permissions import Is_Authenticated
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


from NavyTrials import language,error,settings,common
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
#from . import serializer
#from . import serializer as cSerializer
from configuration.models import Approval
from notification.models import NotificationUser,NotificationUserLog
#from master import models as masterModels
from master import serializer as masterSerializer
from access import models as accessModels
#from accounts import models as accountsModels

from notification import models as notificationModels
from access import models as accessSerializer
#import pandas as pd
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
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission

    def post(self,request, pk = None):

        if "name" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "code" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:

            #print(request.data,"adad")
            if request.data["id"]=="":

                models.Config.objects.create(
                    name = request.data["name"],
                    code = request.data["code"],
                    desc = request.data["desc"],
                    created_by_id = request.user.id,
                    created_ip = Common.get_client_ip(request),
                    status = request.data["status"]
                )
                return Response({"status" :error.context['success_code'], "message":'Config created successfully'}, status=status.HTTP_200_OK)
            else:
                models.Config.objects.filter(id=request.data["id"]).update(
                    name = request.data["name"],
                    code = request.data["code"],
                    desc = request.data["desc"],
                    modified_by_id = request.user.id,
                    modified_ip = Common.get_client_ip(request),
                    status = request.data["status"]
                )

                return Response({"status" :error.context['success_code'], "message":'Config updated successfully'}, status=status.HTTP_200_OK)
