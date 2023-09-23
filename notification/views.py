from functools import reduce
import operator
from pickle import FALSE
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Notification,Smtpconfigure
from .serializer import Notificationserializer,Smtpconfigureserializer
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings                                                                                                                                                       
from django.http import HttpResponse
from twilio.rest import Client
from NavyTrials import language
from .models import Notification,Smtpconfigure,NotificationUser,NotificationUserLog
from .serializer import NotificationUserSerializer
from django.db.models import Q
from NavyTrials import language,error,settings,common
from master.models import TrialTypes,DataAccess
from master import models as masterModels
from master import serializer as masterSerializer
from access import models as accessModels
from access import models as accessSerializer

  
class SmtpconfigureViews(APIView):

    def post(self, request, format=None):
        
        serializer = Smtpconfigureserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "Success", "data": serializer.data}, status=status.HTTP_200_OK)
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationViews(generics.GenericAPIView):

    serializer_class = Notificationserializer

    def post(self,request):
        notification = request.data    
        serializer = Notificationserializer(data = notification)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        notification = serializer.data
        if notification['type'] == 2:
            #notification = Notification.objects.get(to=notification_data['to'])
            # token = RefreshToken.for_user(notification).access_token
            # current_site = get_current_site(request).domain
            # relativeLink = reverse('email-verify')
            # absurl = 'http://'+current_site+relativeLink+"?token"+str(token)
            
            # email_body= 'Hi '+notification['message']+'\n Use below link to verfy your email \n'
            email_body= 'Hi '+notification['message']
            data = {'email_body' : email_body, 'to_email' : notification['to'], 'email_subject':'verify your email'}
            Util.send_email(data)
            return Response({"status" :"success","message":+language.context[language.defaultLang]['email send'], "data" : 'test'}, status=status.HTTP_200_OK)

        else:
           
            message_to_broadcast = ("pink ")
                                                        
            #print('hi')                                            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            for recipient in settings.SMS_BROADCAST_TO_NUMBERS:
                if recipient:
                    client.messages.create(to=recipient,
                                        from_=settings.TWILIO_NUMBER,
                                        body=message_to_broadcast)
            # return HttpResponse("messages sent!", 200)

            return Response({"status" : "success","message":+language.context[language.defaultLang]['sms sent'], "data" : 'test'}, status=status.HTTP_200_OK)

            
class VerifyEmail(generics.GenericAPIView):
    def get(self):
        pass



class getNotifications(APIView):
    
    def post(self,request, pk = None):      
        filter_values = dict(request.GET.items())
        search_string=order_type=order_column=limit_start=limit_end=''
        normal_values=dict()
        array_values=dict()
        if filter_values:
            for key,values in filter_values.items():
                if values.find("[") !=-1 and values.find("]") !=-1:
                    res = values.strip('][').split(',')
                    array_values[key]=(res)
                else:
                    normal_values[key]=(values)

            strings = ['name','description']
            search_string = dict((k, normal_values[k]) for k in strings
                                            if k in normal_values)  
            order_column =  request.GET.get('order_column')
            order_type = request.GET.get('order_type')  
            limit_start = request.GET.get('limit_start')
            limit_end = request.GET.get('limit_end')  


            if order_column is not None:                                      
                normal_values.pop('order_column')
            if order_type is not None: 
                normal_values.pop('order_type')  
            if limit_start is not None: 
                normal_values.pop('limit_start')
            if limit_end is not None: 
                normal_values.pop('limit_end')     

            for key in strings:
                if key in normal_values:
                    normal_values.pop(key)

            if search_string:       
                filter_string = None
                for field in search_string:
                    q = Q(**{"%s__contains" % field: search_string[field] })
                    if filter_string:
                        filter_string = filter_string & q
                    else:
                        filter_string = q
        try:
            user_role_id=request.headers['Authorized-By'] if 'Authorized-By' in request.headers else None
            logList=NotificationUserLog.objects.values('notification_id').filter(user_id=request.user.id,user_role_id=user_role_id)
            logids=(o['notification_id'] for o in logList)

            notificationList=NotificationUser.objects.exclude(id__in=logids)
            if 'Authorized-Role' in request.headers:
                role_code=request.headers['Authorized-Role']
                role_id=request.headers['Authorized-By']
                process_id=request.user.process_id
                #print('process_id',process_id)
                if role_code!='admin':
                    satList=DataAccess.objects.values_list('satellite_unit_id','trial_unit_id').filter(user_id=request.user.id)
                    shipList=masterModels.DataAccessShip.objects.values_list('ship_id').filter(data_access__user_id=request.user.id)
                    ship_ids=(o[0] for o in shipList)
                    satellite_unit_ids=(o[0] for o in satList)
                    trial_unit_ids=(o[1] for o in satList)
                    # satList=DataAccess.objects.values('satellite_unit_id').filter(user_id=request.user.id)
                    # ids=(o['satellite_unit_id'] for o in satList)
                    # notificationList=notificationList.filter(satellite_unit_id__in=ids)
                    if trial_unit_ids:
                        notificationList=notificationList.filter(trial_unit_id__in=trial_unit_ids)
                    if satellite_unit_ids:
                        notificationList=notificationList.filter(satellite_unit_id__in=satellite_unit_ids)
                    if ship_ids:
                        notificationList=notificationList.filter(trial__ship_id__in=ship_ids)
                    notificationList=notificationList.filter((Q(user_role_id=role_id) & Q(process_id=process_id)) | Q(user_role_id=None))
                else:
                    notificationList=notificationList.filter(user_role_id=None)
                notificationList = notificationList.order_by('-id') 
                serializer=NotificationUserSerializer(notificationList, many=True,context = {'request':request})
                return Response({"status":error.context['success_code'], "data": serializer.data}, status=status.HTTP_200_OK)
                    
        except:
            return Response({"status":error.context['error_code'],"message" : "Failed to perform this action"},status=status.HTTP_200_OK)

        lists =NotificationUser.objects.exclude(status='3')
        #lists = lists.order_by('-id') 
        if normal_values:
            lists = lists.filter(reduce(operator.and_, 
                               (Q(**d) for d in [dict([i]) for i in normal_values.items()])))
        if array_values:
            for key,values in array_values.items():
                queries= [Q(**{"%s__contains" % key: value }) for value in values]
                query=queries.pop()
                for item in queries:
                    query |= item
                lists = lists.filter(query)

        if search_string:
            lists = lists.filter(filter_string)

        if order_type is None: 
            if order_column:
                lists = lists.order_by(order_column)  

        elif order_type in 'asc':
            if order_column:
                lists = lists.order_by(order_column)
            else: 
                lists = lists.order_by('id')   

        elif order_type in 'desc':
            if order_column:
                order_column = '-' + str(order_column)
                lists = lists.order_by(order_column)
            else: 
                lists = lists.order_by('-id') 

        if limit_start and limit_end:
                lists = lists[int(limit_start):int(limit_end)]

        elif limit_start:
                lists = lists[int(limit_start):]

        elif limit_end:
                lists = lists[0:int(limit_end)]           
        
        serializer =NotificationUserSerializer(lists, many=True)
        return Response({"status":error.context['success_code'], "data": serializer.data}, status=status.HTTP_200_OK)


class saveNotificationLog(APIView):
    
    def post(self,request, pk = None):
        if 'notification_id' not in request.data:
            return Response({"status":error.context['error_code'],"message" : "notification_id" +language.context[language.defaultLang]['missing'] },status=status.HTTP_200_OK)
        else:
            user_role_id=request.headers['Authorized-By'] if 'Authorized-By' in request.headers else None
            NotificationUserLog.objects.create(notification_id=request.data['notification_id'],user_id=request.user.id,user_role_id=user_role_id)
            return Response({"status":error.context['success_code'], "message": 'Log saved successfully'}, status=status.HTTP_200_OK)