from socketserver import DatagramRequestHandler
from venv import create
from django.db.models import F
from master.models import Command
from rest_framework import serializers
from access.serializer import AccessUserRoleserializer
from . import models
from accounts.serializer import Userserializer

# from master.serializer import (

#     TrialTypesSerializer,
# )
from configuration.models import Approval

from master import models as masterModels
from accounts import models as accountsModels
from access import models as accessModels


class TrialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trials
        fields = "__all__"


# class trialApprovalSerializer(serializers.ModelSerializer):
#     trial = TrialSerializer(read_only=True)
#     approved_role = AccessUserRoleserializer(read_only=True)
#     approved_by = Userserializer(read_only=True)

#     class Meta:
#         model = models.trialApproval
#         fields = "__all__"


# class UserserializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = accountsModels.User
#         fields = (
#             "id",
#             "first_name",
#             "last_name",
#             "loginname",
#         )


# class AccessUserRoleserializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = accessModels.AccessUserRoles
#         fields = (
#             "id",
#             "name",
#             "code",
#         )


# class trialApprovalSerializerList(serializers.ModelSerializer):
#     approved_role = AccessUserRoleserializerForListing(read_only=True)
#     approved_by = UserserializerForListing(read_only=True)

#     class Meta:
#         model = models.trialApproval
#         fields = (
#             "comments",
#             "id",
#             "status",
#             "approved_role",
#             "approved_by",
#             "approved_on",
#             "type",
#         )


class TrialListNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trials
        fields = "__all__"


# class TrialUnitsSerializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = masterModels.TrialUnits
#         fields = (
#             "id",
#             "name",
#         )


# class SatelliteUnitsSerializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = masterModels.SatelliteUnits
#         fields = (
#             "id",
#             "name",
#         )


# class ShipsSerializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = masterModels.Ships
#         fields = (
#             "id",
#             "name",
#         )


# class SectionsSerializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = masterModels.Sections
#         fields = (
#             "id",
#             "name",
#         )


# class EquipmentsSerializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = masterModels.Equipments
#         fields = (
#             "id",
#             "name",
#         )


# class BoilersSerializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = masterModels.Boilers
#         fields = (
#             "id",
#             "name",
#         )


# class TrialTypesSerializerForListing(serializers.ModelSerializer):
#     class Meta:
#         model = masterModels.TrialTypes
#         fields = (
#             "id",
#             "name",
#             "url",
#             "type",
#             "report_url",
#         )


# class TrialListSerializer(serializers.ModelSerializer):
#     trial_unit = TrialUnitsSerializerForListing(read_only=True)
#     satellite_unit = SatelliteUnitsSerializerForListing(read_only=True)
#     ship = ShipsSerializerForListing(read_only=True)
#     # command = CommandSerializer(read_only=True)
#     section = SectionsSerializerForListing(read_only=True)
#     equipment = EquipmentsSerializerForListing(read_only=True)
#     boilers = BoilersSerializerForListing(read_only=True)
#     trial_type = TrialTypesSerializerForListing(read_only=True)
#     created_by = UserserializerForListing(read_only=True)

#     class Meta:
#         model = models.Trials
#         # fields ="__all__"
#         fields = [
#             "id",
#             "trial_number",
#             "created_on",
#             "satellite_unit",
#             "ship",
#             "trial_unit",
#             "trial_type",
#             "created_by",
#             "legacy_data",
#             "ship_initiater",
#             "ship_approver",
#             "trial_initiater",
#             "trial_approver",
#             "approved_level",
#             "section",
#             "equipment",
#             "boilers",
#         ]

# def to_representation(self, instance, request=None):
#     response = super().to_representation(instance)
#     if self.context:
#         request = self.context["request"]
#         user_role_id = request.headers["Authorized-By"]

#         trialApprovals = (
#             models.trialApproval.objects.values(
#                 "status", "approved_on", "comments", "approved_level", "type"
#             )
#             .filter(trial_id=response["id"])
#             .order_by("id")
#         )
#         shipInitiator = [
#             trialApproval
#             for trialApproval in trialApprovals
#             if trialApproval["approved_level"] == 1 and trialApproval["type"] == 1
#         ]
#         shipInitiator = (
#             shipInitiator[len(shipInitiator) - 1] if shipInitiator else None
#         )

#         ship_recommendation = [
#             trialApproval
#             for trialApproval in trialApprovals
#             if trialApproval["approved_level"] == 2 and trialApproval["type"] == 1
#         ]
#         ship_recommendation = (
#             ship_recommendation[len(ship_recommendation) - 1]
#             if ship_recommendation
#             else None
#         )

#         ship_approver = [
#             trialApproval
#             for trialApproval in trialApprovals
#             if trialApproval["approved_level"] == 3 and trialApproval["type"] == 2
#         ]
#         ship_approver = (
#             ship_approver[len(ship_approver) - 1] if ship_approver else None
#         )

#         trial_initiater = [
#             trialApproval
#             for trialApproval in trialApprovals
#             if trialApproval["approved_level"] == 4
#         ]
#         trial_initiater = (
#             trial_initiater[len(trial_initiater) - 1] if trial_initiater else None
#         )

#         trial_recommendation = [
#             trialApproval
#             for trialApproval in trialApprovals
#             if trialApproval["approved_level"] == 5 and trialApproval["type"] == 1
#         ]
#         trial_recommendation = (
#             trial_recommendation[len(trial_recommendation) - 1]
#             if trial_recommendation
#             else None
#         )

#         trial_approver = [
#             trialApproval
#             for trialApproval in trialApprovals
#             if trialApproval["approved_level"] == 6 and trialApproval["type"] == 2
#         ]
#         trial_approver = (
#             trial_approver[len(trial_approver) - 1] if trial_approver else None
#         )

#         response["ship_initiater"] = shipInitiator
#         response["ship_recommendation"] = ship_recommendation
#         response["ship_approver"] = ship_approver
#         response["trial_initiater"] = trial_initiater
#         response["trial_recommendation"] = trial_recommendation
#         response["trial_approver"] = trial_approver
# response['history']=models.trialApproval.objects.values('id','status','comments','approved_on','approved_by__first_name','approved_by__last_name','approved_by__process__name','approved_role__name').filter(trial_id=response['id']).order_by('id')
# response['history']=trialApprovalSerializerList(models.trialApproval.objects.filter(trial_id=response['id']).order_by('id'),many=True).data
# For all approvals
# approvalDataAll=Approval.objects.values('id').filter(trail_unit_id=response['trial_unit']['id'],satellite_unit_id=response['satellite_unit']['id'])
# approvedDataAll=models.trialApproval.objects.values('id').filter(trial_id=response['id'])

# approval={}
# approval['status']='approved' if len(list(approvalDataAll))>0 and len(list(approvalDataAll))==len(list(approvedDataAll)) else 'pending'

# # For particular role and user
# approvalData=Approval.objects.values('id','level').filter(trail_unit_id=response['trial_unit']['id'],satellite_unit_id=response['satellite_unit']['id'],user_role_id=user_role_id).first()
# approvedData=models.trialApproval.objects.values('approved_on','status').filter(trial_id=response['id'],approved_by_id=request.user.id,approved_role_id=user_role_id).first()

# historyData=trialApprovalSerializer(models.trialApproval.objects.filter(trial_id=response['id']),many=True).data

# approval['required']=True if approvalData else False
# approval['level']=approvalData['level'] if approvalData else 0
# approval['approved']=True if approvedData else False
# approval['approved_date']=approvedData['approved_on'] if approvedData else ''
# approval['approval_status']=approvedData['status'] if approvedData else ''
# approval['history']=historyData
# response['approval']=approval

# return response


# # class TempImportSerializer(serializers.ModelSerializer):

# #     class Meta:
# #         model = models.TempImport
# #         fields = "__all__"


# class TempImportDataSerializer(serializers.ModelSerializer):
#     # running_id= TempImportSerializer(read_only=True)
#     class Meta:
#         model = models.TempImportData
#         fields = "__all__"


# # 1
# class HSconvertorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.HSconvertor
#         fields = "__all__"


# class HSconvertorListSerializer(serializers.ModelSerializer):
#     trial = TrialListSerializer(read_only=True)

#     class Meta:
#         model = models.HSconvertor
#         fields = "__all__"


# # 1log
# class HSconvertorlogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.HSconvertorLog
#         fields = "__all__"


# class HSconvertorlogListSerializer(serializers.ModelSerializer):
#     running_id = HSconvertorListSerializer(read_only=True)

#     class Meta:
#         model = models.HSconvertorLog
#         fields = "__all__"
