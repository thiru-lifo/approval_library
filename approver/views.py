from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from . import models


class ConfigCRUD(APIView):

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

            if request.data["id"]==None:

                models.Config.objects.create(
                    name = request.data["name"],
                    code = request.data["code"],
                    desc = request.data["desc"],
                    created_id = request.user.id,
                    created_ip = Common.get_client_ip(request),
                    status = request.data["status"]
                )
                return Response({"status" :error.context['success_code'], "message":'Config created successfully'}, status=status.HTTP_200_OK)
            else:
                models.Config.objects.filter(id=request.data["id"]).update(
                    name = request.data["name"],
                    code = request.data["code"],
                    desc = request.data["desc"],
                    modified_id = request.user.id,
                    modified_ip = Common.get_client_ip(request),
                    status = request.data["status"]
                )

                return Response({"status" :error.context['success_code'], "message":'Config updated successfully'}, status=status.HTTP_200_OK)
