from gettext import Catalog
from importlib.resources import Package
from inspect import Signature
from itertools import product
from operator import mod
from pyexpat import model
from tabnanny import verbose

# from xml.dom.minidom import DocumentType
from django.db import models
from django.db.models.deletion import CASCADE
import phonenumbers

# from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import User
from access.models import AccessUserRoles, ProcessFlow
from datetime import datetime


class Trials(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    # code = models.CharField(max_length=100, blank=True, null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True
    )
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)


# # Approval of trials
# class trialStatus(models.Model):
#     trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)
#     process_flow = models.ForeignKey(ProcessFlow, on_delete=models.CASCADE, null=True)
#     created_on = models.DateTimeField(auto_now_add=True, null=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     created_ip = models.GenericIPAddressField(null=True)


# class trialApproval(models.Model):
#     trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)
#     comments = models.TextField(null=True, blank=True)
#     type = models.SmallIntegerField(
#         choices=((1, "Recommendation"), (2, "Approval")), null=True, blank=True
#     )
#     status = models.SmallIntegerField(
#         choices=((1, "Approved"), (2, "Rejected")), null=True, blank=True
#     )
#     approved_role = models.ForeignKey(
#         AccessUserRoles, on_delete=models.CASCADE, null=True
#     )
#     approved_level = models.SmallIntegerField(null=True)
#     approved_on = models.DateTimeField(auto_now_add=True)
#     approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     approved_ip = models.GenericIPAddressField(null=True)


# # 1
# class HSconvertor(models.Model):
#     trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)


# # # 1log
# class HSconvertorLog(models.Model):
#     running_id = models.ForeignKey(HSconvertor, on_delete=models.CASCADE, null=True)
#     trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)

#     def _str_(self):
#         return self.name

#     class Meta:
#         db_table = "log.HSconvertor"
#         verbose_name = "HSconvertor"
#         verbose_name_plural = "HSconvertor"
