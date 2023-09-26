from functools import reduce
import operator
from telnetlib import STATUS
from django.shortcuts import render
from access import models

# Create your views here.
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenViewBase,
)

from .serializer import (
    MyTokenObtainSerializer,
    MyTokenRefreshSerializer,
    UserListSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from accounts.serializer import Userserializer
from rest_framework import status
from access.views import Common
from log.models import UserLogin
from datetime import datetime
from NavyTrials import language, error
from notification.utils import Util
from django.template import loader
from configuration.models import Templatestable
from django.template import Context, Template
from configuration.models import Configurationtable, RoleConfiguration, Templatestable
from configuration.serializer import Configurationtableserializer
from django.utils.crypto import get_random_string
from access.models import Process, RolesPermissions, AccessUserRoles, UserRoleMapping
from master.models import (
    DataAccess,
    DataAccessShip,
    Department,
    TrialUnits,
    SatelliteUnits,
    Ships,
    ShipSatelliteMapping,
)
from master.serializer import DataAccessSerializerCRUD, DataAccessShipSerializer
from . import models
from . import serializer

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import csv
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render

# from onelogin.saml2.auth import OneLogin_Saml2_Auth
# from onelogin.saml2.settings import OneLogin_Saml2_Settings
# from onelogin.saml2.utils import OneLogin_Saml2_Utils


class MyTokenObtainPairView(TokenViewBase):
    # def post(self, request, *args, **kwargs):
    # print()
    default_error_messages = {
        "no_active_account": "Username or Password does not matched."
    }
    serializer_class = MyTokenObtainSerializer


class MyTokenRefreshView(TokenViewBase):
    serializer_class = MyTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        token = RefreshToken

        if token:
            return Response(
                {
                    "status": error.context["success_code"],
                    "message": language.context[language.defaultLang]["missing"],
                    "token": token,
                }
            )
        else:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": language.context[language.defaultLang][
                        "Incorrect username or password"
                    ],
                }
            )


class CorrectVerificationCode(APIView):
    def post(self, request):
        data = request.data
        if "email" not in data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Email"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "verification_code" not in data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Verification code"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            userAvailable = User.objects.filter(
                email=data["email"], verification_code=data["verification_code"]
            )
            if userAvailable:
                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": language.context[language.defaultLang]["matched"],
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": error.context["error_code"],
                        "message": language.context[language.defaultLang][
                            "incorrect code"
                        ],
                    },
                    status=status.HTTP_200_OK,
                )


class LogoutView(APIView):
    def post(self, request):
        data = request.data
        if "user_id" not in data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            log_browser = request.user_agent.browser.family
            log_version = request.user_agent.browser.version_string
            log_os = request.user_agent.os.family
            log_platform = request.user_agent.device.family
            log_ip = Common.get_client_ip(request)
            log_datetime = datetime.now()
            userlog = UserLogin.objects.create(
                user_id=data["user_id"],
                logon_type="logout",
                log_datetime=log_datetime,
                log_ip=log_ip,
                log_browser=log_browser,
                log_version=log_version,
                log_os=log_os,
                log_platform=log_platform,
            ).save()
            return Response(
                {
                    "status": error.context["success_code"],
                    "message": language.context[language.defaultLang]["logout"],
                },
                status=status.HTTP_200_OK,
            )


class ResendCodeView(APIView):
    def post(self, request):
        data = request.data
        if "user_id" not in data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            user = (
                User.objects.values("id", "verification_code", "email", "loginname")
                .filter(id=data["user_id"])
                .first()
            )

            email_data = {
                "verification_code": user["verification_code"],
                "user_name": user["loginname"],
            }
            template = (
                Templatestable.objects.values(
                    "id", "title", "actual_template", "modified_template"
                )
                .filter(code="VFC")
                .first()
            )
            if template:
                if template["modified_template"]:
                    template = template["modified_template"]
                else:
                    template = template["actual_template"]
                t = Template(template)
                c = Context(email_data)
                html = t.render(c)

            else:
                html = loader.render_to_string(
                    "email/verification-code.html", context=email_data
                )

            Util.send_email(
                {
                    "email_subject": "Your STEMZ Global account verification code",
                    "email_body": html,
                    "to_email": user["email"],
                }
            )
            return Response(
                {
                    "status": error.context["success_code"],
                    "message": language.context[language.defaultLang][
                        "verification code"
                    ],
                },
                status=status.HTTP_200_OK,
            )


class authenticationView(APIView):
    def post(self, request):
        if "user_role_id" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User role id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "user_id" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User id"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            center_id = (
                request.data["center_id"]
                if "center_id" in request.data and request.data["center_id"]
                else 0
            )
            user_role_id = (
                request.data["user_role_id"] if "user_role_id" in request.data else 0
            )
            user_id = request.data["user_id"] if "user_id" in request.data else 0

            user_role_id = request.data["user_role_id"]
            user_id = request.data["user_id"]
            data = {}
            biometricVal = (
                Configurationtable.objects.values("id", "value")
                .filter(code="BM")
                .first()
            )
            if (
                biometricVal
                and biometricVal["value"]
                and biometricVal["value"].lower() == "true"
            ):
                rolePerm = (
                    RoleConfiguration.objects.values("id", "role_id", "config_id")
                    .filter(role_id=user_role_id, config_id=biometricVal["id"])
                    .first()
                )
                if rolePerm:
                    data["biometric"] = True
                    biometric = True
                else:
                    data["biometric"] = False
                    biometric = False
            else:
                data["biometric"] = False
                biometric = False
            # print(bool(biometricVal['value']))
            if biometric:
                userfp = UserFingerIndex.objects.values(
                    "fingerindex__id", "fingerindex__name", "fpdata", "user__id"
                ).filter(user=user_id)

                data["fpdata"] = userfp

            # twofactverify = True
            twofactor = (
                Configurationtable.objects.values("id", "value")
                .filter(code="2FA")
                .first()
            )
            if (
                twofactor
                and twofactor["value"]
                and twofactor["value"].lower() == "true"
            ):
                rolePerm = (
                    RoleConfiguration.objects.values("id", "role_id", "config_id")
                    .filter(role_id=user_role_id, config_id=twofactor["id"])
                    .first()
                )
                if rolePerm:
                    data["twofactor"] = True
                    twofactverify = True
                else:
                    data["twofactor"] = False
                    twofactverify = False
            else:
                data["twofactor"] = False
                twofactverify = False

            if twofactverify:
                template = (
                    Templatestable.objects.values(
                        "id", "title", "actual_template", "modified_template"
                    )
                    .filter(code="VFC")
                    .first()
                )
                vc = get_random_string(
                    length=6, allowed_chars="1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                )
                user = (
                    User.objects.values("id", "verification_code", "email", "loginname")
                    .filter(id=user_id)
                    .first()
                )
                email_data = {"verification_code": vc, "user_name": user["loginname"]}
                User.objects.filter(id=user_id).update(verification_code=vc)
                if template:
                    if template["modified_template"]:
                        template = template["modified_template"]
                    else:
                        template = template["actual_template"]
                    t = Template(template)
                    c = Context(email_data)
                    html = t.render(c)
                else:
                    html = loader.render_to_string(
                        "email/verification-code.html", context=email_data
                    )

                Util.send_email(
                    {
                        "email_subject": "Your STEMZ Global account verification code",
                        "email_body": html,
                        "to_email": user["email"],
                    }
                )
            return Response(
                {"status": error.context["success_code"], "authentication": data},
                status=status.HTTP_200_OK,
            )


class ChangePasswordAPI(APIView):
    def post(self, request):
        if "old_password" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Old password"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "new_password" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "New password"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "new_password2" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Confirm password"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif request.data["new_password"] != request.data["new_password2"]:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Password and confirm password not match"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        else:
            user_id = request.user.id
            old_password = request.data["old_password"]
            new_password = request.data["new_password"]
            user = User.objects.filter(id=user_id).first()
            if not user.check_password(old_password):
                return Response(
                    {
                        "status": error.context["error_code"],
                        "message": "Wrong old password.",
                    },
                    status=status.HTTP_200_OK,
                )

            # set_password also hashes the password that the user will get
            user.set_password(new_password)
            user.save()

            response = {
                "status": error.context["success_code"],
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }
            return Response(response)


class userList(APIView):
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

            strings = ["first_name", "last_name"]
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
                list = User.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = UserListSerializer(list)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except User.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = User.objects.exclude(status=3)
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

        serializer = UserListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class usersCRUD(APIView):
    def post(self, request):
        if "status" not in request.data:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Status"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif (
            "loginname" not in request.data or not request.data["loginname"]
        ) and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Username"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif (
            "email" not in request.data or not request.data["email"]
        ) and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Email"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif (
            "first_name" not in request.data or not request.data["first_name"]
        ) and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "First name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif (
            "last_name" not in request.data or not request.data["last_name"]
        ) and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Last name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif (
            ("password" not in request.data or not request.data["password"])
            and request.data["status"] != 3
            and request.data["id"] == ""
        ):
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Password"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif (
            "user_role_id" not in request.data or not request.data["user_role_id"]
        ) and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "User role"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        # elif ('data_access' not in request.data or not request.data['data_access']) and request.data['status'] != 3:
        #     return Response({"status":error.context['error_code'],"message" : "Data access" +language.context[language.defaultLang]['missing'] },status=status.HTTP_200_OK)
        else:
            # try:
            # DELETE OPERATION
            if request.data["status"] == 3 and request.data["id"] != "":
                User.objects.filter(id=request.data["id"]).update(status=3)
                # User.objects.filter(id=request.data['id']).delete()
                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": "User deleted successfully",
                    },
                    status=status.HTTP_200_OK,
                )

            # UPDATE OPERATION
            if (
                "id" in request.data
                and request.data["id"] != ""
                and request.data["id"] is not None
            ):
                user = User.objects.filter(id=request.data["id"]).first()
                # #print(request.data['password'])
                # user.set_password(request.data['password'])
                # user.save()
                User.objects.filter(id=request.data["id"]).update(
                    loginname=request.data["loginname"],
                    email=request.data["email"],
                    first_name=request.data["first_name"],
                    last_name=request.data["last_name"],
                    process_id=request.data["process"],
                    department_id=request.data["department"],
                    designation=request.data["designation"],
                )
                if request.data["user_role_id"]:
                    UserRoleMapping.objects.filter(user_id=request.data["id"]).delete()
                    for user_role in request.data["user_role_id"]:
                        UserRoleMapping(
                            user_id=request.data["id"],
                            user_role_id=user_role,
                            process_id=request.data["process"],
                        ).save()


                return Response(
                    {
                        "status": error.context["success_code"],
                        "message": "User updated successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # INSERT OPERATION
                saveserialize = Userserializer(data=request.data)
                if saveserialize.is_valid():
                    saveserialize.save()
                    User.objects.filter(id=saveserialize.data["id"]).update(
                        process_id=request.data["process"]
                    )
                    user = User.objects.filter(id=saveserialize.data["id"]).first()
                    user.set_password(request.data["password"])
                    user.save()

                    if request.data["user_role_id"]:
                        UserRoleMapping.objects.filter(
                            user_id=saveserialize.data["id"]
                        ).delete()
                        for user_role in request.data["user_role_id"]:
                            UserRoleMapping(
                                user_id=saveserialize.data["id"],
                                user_role_id=user_role,
                                process_id=request.data["process"],
                            ).save()
                    return Response(
                        {
                            "status": error.context["success_code"],
                            "message": "New user"
                            + language.context[language.defaultLang]["insert"],
                            "data": saveserialize.data,
                        },
                        status=status.HTTP_200_OK,
                    )
          
            return Response(
                        {
                            "status": error.context["error_code"],
                            "message": error.serializerError(saveserialize),
                        },
                        status=status.HTTP_200_OK,
                    )
        # except:
        #   return Response({"status":error.context['error_code'],"message" : "Failed to perform this action"},status=status.HTTP_200_OK)


from django.contrib.auth.hashers import make_password, check_password


class userImport(APIView):
    def post(self, request, pk=None):
        request_file = request.data["user_import"]
        dir_storage = "static/import_excel"
        fs = FileSystemStorage(location=dir_storage)
        filename = fs.save(request_file.name, request_file)
        if (
            os.path.splitext(request_file.name)[1] == ".xls"
            or os.path.splitext(request_file.name)[1] == ".xlsx"
            or os.path.splitext(request_file.name)[1] == ".csv"
        ):
            excel_folder = os.path.join(settings.BASE_DIR, "static/import_excel/")
            # print("cvsdd",request_file)
            # read_file = pd.read_csv(request_file,delim_whitespace=True)

            # print("cvs",read_file)
            # read_file(excel_folder +'import_excel_file.csv')
            # print("hlo",excel_folder+filename)
            fhand = open(excel_folder + filename)
        else:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "File format not supported (Xls and Xlsx only allowed)",
                }
            )
        reader = csv.reader(fhand)
        next(reader)
        request_data = dict()
        if reader:
            for row in reader:
                # print("row", row)
                lower = row[10].lower()
                if lower == "true":
                    row[10] = True
                else:
                    row[10] = False
                created_ip = Common.get_client_ip(request)
                created_by = request.user.id
                psw = row[6]
                if psw:
                    encryptedpassword = make_password(password=row[6])
                    checkpassword = check_password(row[6], encryptedpassword)
                else:
                    encryptedpassword = make_password(password="navy@123")
                    checkpassword = check_password("navy@123", encryptedpassword)

                Userprocess = (
                    Process.objects.values_list("id", flat=True)
                    .filter(name=row[8])
                    .first()
                )
                userAcc_id = User.objects.create(
                    first_name=row[1],
                    last_name=row[2],
                    loginname=row[3],
                    designation=row[4],
                    email=row[5],
                    ad_user=row[10],
                    process_id=Userprocess,
                    password=encryptedpassword,
                )
                # print("userAcc_id", userAcc_id)
                department1 = (
                    Department.objects.values("id", "name", "code")
                    .filter(code=row[7])
                    .first()
                )
                # print("department1", department1)
                accessUser_id = (
                    AccessUserRoles.objects.values_list("id", flat=True)
                    .filter(name=row[9])
                    .first()
                )
                # print("accessUser_id", accessUser_id)

                userMapping = UserRoleMapping.objects.create(
                    user_role_id=accessUser_id,
                    user_id=userAcc_id.id,
                    process_id=Userprocess,
                )

                trial_id = (
                    TrialUnits.objects.values_list("id", flat=True)
                    .filter(code=row[11])
                    .first()
                )
                # print("trial_id", trial_id)

                sat_id = (
                    SatelliteUnits.objects.values_list("id", flat=True)
                    .filter(code=row[12], trial_unit_id=trial_id)
                    .first()
                )
                # print("sat_id", sat_id)
                if sat_id == None:
                    sat_id = (
                        SatelliteUnits.objects.values_list("id", flat=True)
                        .filter(trial_unit_id=trial_id)
                        .first()
                    )
                # print("sat", sat_id)
                ship_id = (
                    Ships.objects.values_list("id", flat=True)
                    .filter(code=row[13], trial_unit_id=trial_id)
                    .first()
                )
                # print("ship", ship_id)
                if ship_id == None:
                    ship_id = (
                        ShipSatelliteMapping.objects.values_list("ship_id", flat=True)
                        .filter(satellite_unit_id=sat_id)
                        .first()
                    )
                # print("ship_id", ship_id)
                data_access_id = DataAccess.objects.create(
                    trial_unit_id=trial_id,
                    user_id=userAcc_id.id,
                    satellite_unit_id=sat_id,
                )
                # print('data_access_id',data_access_id)
                data_access_ship_id = DataAccessShip.objects.create(
                    data_access_id=data_access_id.id, ship_id=ship_id
                )
                # print('data_access_ship_id',data_access_ship_id)
            return Response(
                {
                    "status": error.context["success_code"],
                    "message": "User imported successfully",
                }
            )

    # SAML


# def init_saml_auth(req):
#    auth = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)
#    return auth


def prepare_django_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    result = {
        "https": "on" if request.is_secure() else "off",
        "http_host": request.META["HTTP_HOST"],
        "script_name": request.META["PATH_INFO"],
        "server_port": request.META["SERVER_PORT"],
        "get_data": request.GET.copy(),
        "post_data": request.POST.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        "query_string": request.META["QUERY_STRING"],
    }
    return result


def adcheck(request):
    req = prepare_django_request(request)

    auth = init_saml_auth(req)
    errors = []
    error_reason = None
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    print("req", req)
    print("auth", auth)

    if "sso" in req["get_data"]:
        return HttpResponseRedirect(auth.login())
        # If AuthNRequest ID need to be stored in order to later validate it, do instead
        # sso_built_url = auth.login()
        # request.session['AuthNRequestID'] = auth.get_last_request_id()
        # return HttpResponseRedirect(sso_built_url)
    elif "sso2" in req["get_data"]:
        return_to = OneLogin_Saml2_Utils.get_self_url(req) + reverse("attrs")
        return HttpResponseRedirect(auth.login(return_to))
    elif "slo" in req["get_data"]:
        name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
        if "samlNameId" in request.session:
            name_id = request.session["samlNameId"]
        if "samlSessionIndex" in request.session:
            session_index = request.session["samlSessionIndex"]
        if "samlNameIdFormat" in request.session:
            name_id_format = request.session["samlNameIdFormat"]
        if "samlNameIdNameQualifier" in request.session:
            name_id_nq = request.session["samlNameIdNameQualifier"]
        if "samlNameIdSPNameQualifier" in request.session:
            name_id_spnq = request.session["samlNameIdSPNameQualifier"]

        return HttpResponseRedirect(
            auth.logout(
                name_id=name_id,
                session_index=session_index,
                nq=name_id_nq,
                name_id_format=name_id_format,
                spnq=name_id_spnq,
            )
        )

        #  If LogoutRequest ID need to be stored in order to later validate it, do instead
        # slo_built_url = auth.logout(name_id=name_id, session_index=session_index)
        # request.session['LogoutRequestID'] = auth.get_last_request_id()
        # return HttpResponseRedirect(slo_built_url)
    elif "acs" in req["get_data"]:
        request_id = None
        if "AuthNRequestID" in request.session:
            request_id = request.session["AuthNRequestID"]

        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()

        if not errors:
            if "AuthNRequestID" in request.session:
                del request.session["AuthNRequestID"]
            request.session["samlUserdata"] = auth.get_attributes()
            request.session["samlNameId"] = auth.get_nameid()
            request.session["samlNameIdFormat"] = auth.get_nameid_format()
            request.session["samlNameIdNameQualifier"] = auth.get_nameid_nq()
            request.session["samlNameIdSPNameQualifier"] = auth.get_nameid_spnq()
            request.session["samlSessionIndex"] = auth.get_session_index()
            if (
                "RelayState" in req["post_data"]
                and OneLogin_Saml2_Utils.get_self_url(req)
                != req["post_data"]["RelayState"]
            ):
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the req['post_data']['RelayState'] is a trusted URL.
                return HttpResponseRedirect(
                    auth.redirect_to(req["post_data"]["RelayState"])
                )
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()
    elif "sls" in req["get_data"]:
        request_id = None
        if "LogoutRequestID" in request.session:
            request_id = request.session["LogoutRequestID"]
        dscb = lambda: request.session.flush()
        url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                # To avoid 'Open Redirect' attacks, before execute the redirection confirm
                # the value of the url is a trusted URL.
                return HttpResponseRedirect(url)
            else:
                success_slo = True
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    if "samlUserdata" in request.session:
        paint_logout = True
        if len(request.session["samlUserdata"]) > 0:
            attributes = request.session["samlUserdata"].items()

    return render(
        request,
        "index.html",
        {
            "errors": errors,
            "error_reason": error_reason,
            not_auth_warn: not_auth_warn,
            "success_slo": success_slo,
            "attributes": attributes,
            "paint_logout": paint_logout,
        },
    )


def attrs(request):
    paint_logout = False
    attributes = False

    if "samlUserdata" in request.session:
        paint_logout = True
        if len(request.session["samlUserdata"]) > 0:
            attributes = request.session["samlUserdata"].items()

    return render(
        request,
        "attrs.html",
        {"paint_logout": paint_logout, "attributes": attributes},
    )


def metadata(request):
    # req = prepare_django_request(request)
    # auth = init_saml_auth(req)
    # saml_settings = auth.get_settings()
    saml_settings = OneLogin_Saml2_Settings(
        settings=None,
        custom_base_path=settings.SAML_FOLDER,
        sp_validation_only=True,
    )
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type="text/xml")
    else:
        resp = HttpResponseServerError(content=", ".join(errors))
    return resp
