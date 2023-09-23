from django.db import models
import os
from twilio.rest import Client
from master.models import TrialUnits,SatelliteUnits
from access.models import AccessUserRoles,Process
from transaction.models import Trials
from accounts.models import User

class NotificationUser(models.Model):

    trial_unit =models.ForeignKey(TrialUnits,on_delete=models.CASCADE)
    satellite_unit =models.ForeignKey(SatelliteUnits,on_delete=models.CASCADE)
    user_role =models.ForeignKey(AccessUserRoles,on_delete=models.CASCADE,null=True,blank=True)
    process =models.ForeignKey(Process,on_delete=models.CASCADE,null=True,blank=True)
    trial =models.ForeignKey(Trials,on_delete=models.CASCADE)
    message =models.TextField()
    created_on = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'notification.user_notifications'
        verbose_name = "User Notification"
        verbose_name_plural = "User Notifications"

class NotificationUserLog(models.Model):

    notification =models.ForeignKey(NotificationUser,on_delete=models.CASCADE)
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    user_role =models.ForeignKey(AccessUserRoles,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'notification.user_notifications_log'
        verbose_name = "User Notification Log"
        verbose_name_plural = "User Notifications Log"

class Notification(models.Model):

    title = models.CharField(max_length= 100)
    type = models.SmallIntegerField(choices=((1,'SMS'),(2,'Email'), (3,'Internet'),))
    subject = models.CharField(max_length= 50, null= True, blank= True)
    message = models.CharField(max_length= 200)
    to =models.TextField()
    cc = models.EmailField(null= True, blank= True)
    bcc = models.EmailField(null= True, blank= True)
    attachment = models.FileField(null= True, blank= True, upload_to='media/')
    created_on = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'notify'
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"


    # def save(self, *args, **kwargs):
    #     #if test_result is less than 80 execute this
    #    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    #    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    #    client = Client(account_sid, auth_token)

    #    message = client.messages.create(
    #                                 body=f'Hi there-{self.to}',
    #                                 from_='+19108123259',
    #                                 to='+919944632479'
    #                             )

    #    #print(message.sid)   

class Smtpconfigure(models.Model):
    email_use_tls = models.BooleanField((u'EMAIL_USE_TLS'),default=True)
    email_host = models.CharField((u'EMAIL_HOST'),max_length=1024)
    email_host_user = models.CharField((u'EMAIL_HOST_USER'),max_length=255)
    email_host_password = models.CharField((u'EMAIL_HOST_PASSWORD'),max_length=255)
    email_port = models.PositiveSmallIntegerField((u'EMAIL_PORT'),default=587)

    def __str__(self):
        return self.email_host_user

    class Meta:
        db_table = 'smptconfigure'
