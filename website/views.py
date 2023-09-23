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

from master.models import (
    TrialUnits,
)
from .serializer import (
    PagesSerializer,
    PagesListSerializer,
    SlidersSerializer,
    SlidersListSerializer,
    ContactSerializer,
)
from NavyTrials import language, error
from django.db.models import Count
from . import models

from NavyTrials import language, error, settings, common
from access.views import Common

# from Glosys import error

from django.db.models.functions import TruncMonth
from django.db.models import Count

from rest_framework_simplejwt.views import (
    TokenViewBase,
)
from master.models import (
    TrialUnits,
)


class PagesList(APIView):
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

            strings = ["page_title", "page_content", "page_slug"]
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
                    models.Pages.objects.filter(pk=pk).exclude(page_status="3").get()
                )
                serializeobj = PagesListSerializer(lists)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Pages.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Pages"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.Pages.objects.exclude(page_status="3")
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

        serializer = PagesListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class PagesCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Pages.objects.get(pk=pk)
        except models.Pages.DoesNotExist:
            raise Http404

    def post(self, request, pk=None):
        if "trial_unit" not in request.data and request.data["page_status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Trial unit"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )
        elif "page_title" not in request.data and request.data["page_status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )

        else:
            if "id" in request.data:
                pk = request.data["id"]
                request.data._mutable = True
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk or pk == "null":
                    duplicate_page_title = (
                        models.Pages.objects.values("page_title")
                        .filter(page_title=request.data["page_title"])
                        .exclude(page_status=3)
                    )

                    if duplicate_page_title:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit page_title"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = PagesSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New page"
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
                    if request.data["page_status"] != 3:
                        duplicate_page_title = (
                            models.Pages.objects.values(
                                "id", "page_title", "page_status"
                            )
                            .filter(page_title=request.data["page_title"])
                            .exclude(Q(id=request.data["id"]) | Q(page_status=3))
                        )
                        if duplicate_page_title:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit page_title"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = PagesSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Page"
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


class SlidersList(APIView):
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

            strings = ["title", "description"]
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
                lists = models.Sliders.objects.filter(pk=pk).exclude(status="3").get()
                serializeobj = SlidersListSerializer(lists)
                return Response(
                    {
                        "status": error.context["success_code"],
                        "data": serializeobj.data,
                    },
                    status=status.HTTP_200_OK,
                )

        except models.Sliders.DoesNotExist:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Sliders"
                    + language.context[language.defaultLang]["dataNotFound"],
                },
                status=status.HTTP_200_OK,
            )

        lists = models.Sliders.objects.exclude(status="3").order_by("sequence")
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

        serializer = SlidersListSerializer(lists, many=True)
        return Response(
            {"status": error.context["success_code"], "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class SlidersCRUD(APIView):
    def get_object(self, pk):
        try:
            return models.Sliders.objects.get(pk=pk)
        except models.Sliders.DoesNotExist:
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
        elif "title" not in request.data and request.data["status"] != 3:
            return Response(
                {
                    "status": error.context["error_code"],
                    "message": "Name"
                    + language.context[language.defaultLang]["missing"],
                },
                status=status.HTTP_200_OK,
            )

        else:
            if "id" in request.data:
                pk = request.data["id"]
                request.data._mutable = True
                created_ip = Common.get_client_ip(request)
                request.data["created_ip"] = created_ip
                request.data["created_by"] = request.user.id

                if not pk or pk == "null":
                    duplicate_title = (
                        models.Sliders.objects.values("title")
                        .filter(title=request.data["title"])
                        .exclude(status=3)
                    )

                    if duplicate_title:
                        return Response(
                            {
                                "status": error.context["error_code"],
                                "message": language.context[language.defaultLang][
                                    "exit title"
                                ],
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        saveserialize = SlidersSerializer(data=request.data)
                        if saveserialize.is_valid():
                            saveserialize.save()
                            return Response(
                                {
                                    "status": error.context["success_code"],
                                    "message": "New slider"
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
                        duplicate_title = (
                            models.Sliders.objects.values("id", "title", "status")
                            .filter(title=request.data["title"])
                            .exclude(Q(id=request.data["id"]) | Q(status=3))
                        )
                        if duplicate_title:
                            return Response(
                                {
                                    "status": error.context["error_code"],
                                    "message": language.context[language.defaultLang][
                                        "exit title"
                                    ],
                                },
                                status=status.HTTP_200_OK,
                            )
                    request.data["modified_ip"] = Common.get_client_ip(request)
                    request.data["modified_by"] = request.user.id

                    list = self.get_object(pk)

                    saveserialize = SlidersSerializer(
                        list, data=request.data, partial=True
                    )
                    if saveserialize.is_valid():
                        saveserialize.save()
                        return Response(
                            {
                                "status": error.context["success_code"],
                                "message": "Slider"
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


# contact-us get and post api


class ContactViewList(APIView):
    def get(self, request):
        data = {}

        contacts = models.Contact.objects.filter(status=1).order_by("-id")

        serializer = ContactSerializer(contacts, many=True)

        data["status"] = 1
        data["data"] = serializer.data
        return Response(data, status=status.HTTP_200_OK)


class ContactViewPOST(TokenViewBase):
    def post(self, request):
        # serializer = ContactSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        name = request.POST.get("name", None)
        email = request.POST.get("email", None)
        mobile = request.POST.get("mobile", None)
        message = request.POST.get("message", None)
        trial_unit_name = request.POST.get("trial_unit", "55")

        if name and email and mobile and message and trial_unit_name:
            contact_obj = models.Contact(
                name=name,
                email=email,
                mobile=mobile,
                message=message,
                trial_unit=TrialUnits.objects.filter(name=trial_unit_name).first(),
            )
            contact_obj.save()
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(
            {"error": "all field required."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
