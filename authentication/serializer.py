from ast import Try
import email
from email import utils
from random import random
from unittest.util import _MAX_LENGTH
from NavyTrials import error, settings
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from rest_framework.permissions import AllowAny
from django.utils.crypto import get_random_string
from notification.utils import Util
from notification.models import Smtpconfigure
from django.template import loader
from accounts.models import User
from django.http import JsonResponse
from configuration.models import Configurationtable, RoleConfiguration, Templatestable
from configuration.serializer import Configurationtableserializer
from access.views import Common
from log.models import UserLogin
from datetime import datetime
from access.models import RolesPermissions, AccessUserRoles, UserRoleMapping
from django.template import Context, Template
from django.shortcuts import render
import requests
from access.serializer import UserRoleMappingSerializer, Processserializer
from master.models import (
    DataAccess,
    DataAccessShip,
    SatelliteUnits,
    ShipSatelliteMapping,
    Ships,
)
from master.serializer import DataAccessSerializer, DepartmentSerializer
from NavyTrials.encryption import AESify

aes = AESify(block_len=16, salt_len=4)


def decode_ldap_response(dic):
    if isinstance(dic, bytes):
        try:
            return dic.decode("utf-8")
        except:
            return dic
    elif isinstance(dic, dict):
        for key in dic:
            dic[key] = decode_ldap_response(dic[key])
        return dic
    elif isinstance(dic, list):
        # new_l = []
        # for e in dic:
        #     new_l.append(decode_ldap_response((e)))
        # return(new_l)
        return decode_ldap_response(dic[0])
    else:
        return dic


class MyTokenObtainSerializer(TokenObtainPairSerializer):
    permission_classes = (AllowAny,)
    loginname = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True, write_only=True)
    fpdata = serializers.CharField(max_length=255, required=True)
    # verification_code = serializers.CharField(max_length= 6)

    default_error_messages = {"Error": "Incorrect username or password"}

    def to_internal_value(self, data):
        # print("test")
        loginname = data.get("loginname")
        password = data.get("password")
        # print(password)
        """
        Validate Password.
        """
        if not password or not loginname:
            raise serializers.ValidationError(
                {"status": "error", "message": "Incorrect username or password"}
            )
        return data

    def validate(self, attrs):
        try:
            attrs._mutable = True
        except:
            print("12344")

        try:
            attrs["password"] = aes.decrypt(attrs["password"])
        except:
            attrs["password"] = attrs["password"]

        userDet = (
            User.objects.values("ad_user").filter(loginname=attrs["loginname"]).first()
        )
        testUsers = userDet["ad_user"] if userDet else True
        if settings.LDAP_AUTH and testUsers == True:
            import ldap

            try:
                # build a client
                userAttrs = attrs
                ldap_client = ldap.initialize(settings.LDAP_URL)
                # perform a synchronous bind
                ldap_client.set_option(ldap.OPT_REFERRALS, 0)
                ldap_client.simple_bind_s(
                    "{}@hq.indiannavy.mil".format(attrs["loginname"]), attrs["password"]
                )

                base = "dc=hq,dc=indiannavy,dc=mil"
                scope = ldap.SCOPE_SUBTREE
                filter = (
                    "(&(objectClass=user)(sAMAccountName=" + attrs["loginname"] + "))"
                )
                displ_attrs = ["*"]

                r = ldap_client.search_s(base, scope, filter, displ_attrs)
                result = r[0][1]

                userDetails = decode_ldap_response(result)
                if User.objects.filter(loginname=attrs["loginname"]).count() > 0:
                    user = User.objects.filter(loginname=attrs["loginname"]).first()
                    user.set_password(attrs["password"])
                    user.save()

                    # User mapping Insert
                    userMapping = UserRoleMapping()
                    userMapping.user_role_id = 3
                    userMapping.user_id = user.id
                    userMapping.process_id = 2
                    userMapping.save()

                    # Sat  Trialunits based filter
                    sat_id = (
                        SatelliteUnits.objects.values_list("id", flat=True)
                        .filter(trial_unit_id=1)
                        .first()
                    )
                    # Ship_id  Trialunits based filter
                    ship_id = (
                        ShipSatelliteMapping.objects.values_list("ship_id", flat=True)
                        .filter(satellite_unit_id=sat_id)
                        .first()
                    )

                    # DataAccess Insert
                    data_access = DataAccess()
                    data_access.trial_unit_id = 1
                    data_access.user_id = user.id
                    data_access.satellite_unit_id = sat_id
                    data_access.save()

                    # DataAccessShip Insert
                    data_access_ship = DataAccessShip()
                    data_access_ship.data_access_id = data_access.id
                    data_access_ship.ship_id = ship_id
                    data_access_ship.save()
                else:
                    user = User()
                    user.loginname = attrs["loginname"]
                    user.first_name = userDetails["givenName"]
                    user.last_name = userDetails["givenName"]
                    user.email = attrs["loginname"] + "@hq.indiannavy.mil"
                    user.ad_user = True
                    user.staff = False
                    user.admin = False
                    user.status = 1
                    user.process_id = 2
                    user.department_id = 2
                    user.is_active = True
                    user.set_password(attrs["password"])
                    user.save()

                    # User mapping Insert
                    userMapping = UserRoleMapping()
                    userMapping.user_role_id = 3
                    userMapping.user_id = user.id
                    userMapping.process_id = 2
                    userMapping.save()

                    # Sat  Trialunits based filter
                    sat_id = (
                        SatelliteUnits.objects.values_list("id", flat=True)
                        .filter(trial_unit_id=1)
                        .first()
                    )
                    # Ship_id  Trialunits based filter
                    ship_id = (
                        ShipSatelliteMapping.objects.values_list("ship_id", flat=True)
                        .filter(satellite_unit_id=sat_id)
                        .first()
                    )

                    # DataAccess Insert
                    data_access = DataAccess()
                    data_access.trial_unit_id = 1
                    data_access.user_id = user.id
                    data_access.satellite_unit_id = sat_id
                    data_access.save()

                    # DataAccessShip Insert
                    data_access_ship = DataAccessShip()
                    data_access_ship.data_access_id = data_access.id
                    data_access_ship.ship_id = ship_id
                    data_access_ship.save()

            except ldap.SERVER_DOWN as e:
                return {
                    "status": error.context["error_code"],
                    "message": "AD server is down",
                }
            except ldap.INVALID_CREDENTIALS:
                ldap_client.unbind()
                return {
                    "status": error.context["error_code"],
                    "message": "Incorrect username or password",
                }
                print("LDAP credentials incorrect!")

        data = super().validate(attrs)
        if data == "False":
            return {"status": "Error", "message": "Incorrect username or password"}

        log_browser = self.context["request"].user_agent.browser.family
        log_version = self.context["request"].user_agent.browser.version_string
        log_os = self.context["request"].user_agent.os.family
        log_platform = self.context["request"].user_agent.device.family
        log_ip = Common.get_client_ip(self.context["request"])
        log_datetime = datetime.now()

        refresh = self.get_token(self.user)

        list = UserRoleMapping.objects.filter(user_id=self.user.id)
        roleSerializer = UserRoleMappingSerializer(list, many=True)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["user_id"] = self.user.id
        data["role_center"] = roleSerializer.data
        data["user_email"] = self.user.email
        data["first_name"] = self.user.first_name
        data["last_name"] = self.user.last_name
        data["process_id"] = self.user.process_id
        data["department_id"] = self.user.department_id
        data["designation"] = self.user.designation

        userlog = UserLogin.objects.create(
            user_id=self.user.id,
            logon_type="login",
            log_datetime=log_datetime,
            log_ip=log_ip,
            log_browser=log_browser,
            log_version=log_version,
            log_os=log_os,
            log_platform=log_platform,
        ).save()

        user_fields = {"loginname": self.user.loginname, "email": self.user.email}

        configList = Configurationtable.objects.filter(status=1)
        configuration = Configurationtableserializer(configList, many=True)
        data["configuration"] = configuration.data

        return data


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super(MyTokenRefreshSerializer, self).validate(attrs)
        decoded_payload = token_backend.decode(data["access"], verify=True)
        user_name = decoded_payload["loginname"]
        # add filter query
        data.update({"user": self.user.user_name})
        return data


class UserListSerializer(serializers.ModelSerializer):
    process = Processserializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def to_representation(self, instance, appointment_id=None):
        response = super().to_representation(instance)
        response["roles"] = UserRoleMappingSerializer(
            UserRoleMapping.objects.filter(user_id=response["id"]), many=True
        ).data
        response["data_access"] = DataAccessSerializer(
            DataAccess.objects.filter(user_id=response["id"]), many=True
        ).data
        return response
