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
from master.models import (
    Boilers,
    Command,
    TrialUnits,
    SatelliteUnits,
    Ships,
    Sections,
    Equipments,
    TrialTypes,
)
from datetime import datetime


class Trials(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    command = models.ForeignKey(
        Command, on_delete=models.CASCADE, null=True, blank=True
    )
    satellite_unit = models.ForeignKey(
        SatelliteUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    ship = models.ForeignKey(Ships, on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(
        Sections, on_delete=models.CASCADE, null=True, blank=True
    )
    equipment = models.ForeignKey(
        Equipments, on_delete=models.CASCADE, null=True, blank=True
    )
    boilers = models.ForeignKey(
        Boilers,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    trial_type = models.ForeignKey(
        TrialTypes, on_delete=models.CASCADE, null=True, blank=True
    )
    trial_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True
    )
    ship_initiater = models.SmallIntegerField(null=True, blank=True)
    ship_recommender = models.SmallIntegerField(null=True, blank=True)
    ship_approver = models.SmallIntegerField(null=True, blank=True)
    trial_initiater = models.SmallIntegerField(null=True)
    trial_recommender = models.SmallIntegerField(null=True)
    trial_approver = models.SmallIntegerField(null=True)
    created_on = models.DateTimeField(default=datetime.now, blank=True)
    trial_date = models.DateField(blank=True, null=True)
    legacy_data = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)
    approved_level = models.SmallIntegerField(default=1)
    sync = models.BooleanField(default=False)


class PendingTempChart(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    total = models.TextField(null=True, blank=True)
    created_on_month = models.TextField(null=True, blank=True)

    def _str_(self):
        return self.name

    class Meta:
        db_table = "PendingTempChart"
        verbose_name = "PendingTempChart"
        verbose_name_plural = "PendingTempChart"


class ApprovedTempChart(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    total = models.TextField(null=True, blank=True)
    created_on_month = models.TextField(null=True, blank=True)

    def _str_(self):
        return self.name

    class Meta:
        db_table = "ApprovedTempChart"
        verbose_name = "ApprovedTempChart"
        verbose_name_plural = "ApprovedTempChart"


class GtttDelhiTempChart(models.Model):
    trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True, blank=True)
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    command = models.ForeignKey(
        Command, on_delete=models.CASCADE, null=True, blank=True
    )
    satellite_unit = models.ForeignKey(
        SatelliteUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    ship = models.ForeignKey(Ships, on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(
        Sections, on_delete=models.CASCADE, null=True, blank=True
    )
    equipment = models.ForeignKey(
        Equipments, on_delete=models.CASCADE, null=True, blank=True
    )
    created_on = models.DateTimeField(default=datetime.now, null=True, blank=True)
    # Ehm Ftple Delhi Four form
    Hot_Start_Max_Ex_Gas_Temp_GT_1 = models.IntegerField(null=True, blank=True)
    Hot_Start_Max_Ex_Gas_Temp_GT_2 = models.IntegerField(null=True, blank=True)
    Hot_Start_Max_Ex_Gas_Temp_GT_3 = models.IntegerField(null=True, blank=True)
    Hot_Start_Max_Ex_Gas_Temp_GT_4 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Five
    GTs_Ex_Gas_Temp_Idling_GT_1 = models.IntegerField(null=True, blank=True)
    GTs_Ex_Gas_Temp_Idling_GT_2 = models.IntegerField(null=True, blank=True)
    GTs_Ex_Gas_Temp_Idling_GT_3 = models.IntegerField(null=True, blank=True)
    GTs_Ex_Gas_Temp_Idling_GT_4 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Six
    CTP_Ex_Gas_Temp_GT_1 = models.IntegerField(null=True, blank=True)
    CTP_Ex_Gas_Temp_GT_2 = models.IntegerField(null=True, blank=True)
    Slip_Exh_Gas_Temp_GT_1 = models.IntegerField(null=True, blank=True)
    Slip_Exh_Gas_Temp_GT_2 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Seven
    Ser_log_Ex_Gas_Temp_M_GT_3 = models.IntegerField(null=True, blank=True)
    Ser_log_Ex_Gas_Temp_M_GT_4 = models.IntegerField(null=True, blank=True)
    Slip_Exh_Gas_Temp_GT3 = models.IntegerField(null=True, blank=True)
    Slip_Exh_Gas_Temp_GT4 = models.IntegerField(null=True, blank=True)
    HPC_RPM_6900_Ex_Gas_Temp_M_GT_1 = models.IntegerField(null=True, blank=True)
    HPC_RPM_6900_Ex_Gas_Temp_M_GT_2 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Eight
    HPC_RPM_6900_Slip_Exh_Gas_Temp_GT_1 = models.IntegerField(null=True, blank=True)
    HPC_RPM_6900_Slip_Exh_Gas_Temp_GT_2 = models.IntegerField(null=True, blank=True)
    HPC_RPM_6900_Ex_Gas_Temp_M_GT_3 = models.IntegerField(null=True, blank=True)
    HPC_RPM_6900_Ex_Gas_Temp_M_GT_4 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Nine
    HPC_RPM_6900_Slip_Exh_Gas_Temp_GT_3 = models.IntegerField(null=True, blank=True)
    HPC_RPM_6900_Slip_Exh_Gas_Temp_GT_4 = models.IntegerField(null=True, blank=True)
    HPC_RPM_7400_Ex_Gas_Temp_M_GT_1 = models.IntegerField(null=True, blank=True)
    HPC_RPM_7400_Ex_Gas_Temp_M_GT_2 = models.IntegerField(null=True, blank=True)
    HPC_RPM_7400_Slip_Exh_Gas_Temp_GT_1 = models.IntegerField(null=True, blank=True)
    HPC_RPM_7400_Slip_Exh_Gas_Temp_GT_2 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Ten
    HPC_RPM_7400_Ex_Gas_Temp_M_GT_3 = models.IntegerField(null=True, blank=True)
    HPC_RPM_7400_Ex_Gas_Temp_M_GT_4 = models.IntegerField(null=True, blank=True)
    HPC_RPM_7400_Slip_Exh_Gas_Temp_GT_3 = models.IntegerField(null=True, blank=True)
    HPC_RPM_7400_Slip_Exh_Gas_Temp_GT_4 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Eleven
    Full_Power_Run_Ex_Gas_Temp_M_GT_1 = models.IntegerField(null=True, blank=True)
    Full_Power_Run_Ex_Gas_Temp_M_GT_2 = models.IntegerField(null=True, blank=True)
    Full_Power_Run_Slip_Exh_Gas_Temp_GT_1 = models.IntegerField(null=True, blank=True)
    Full_Power_Run_Slip_Exh_Gas_Temp_GT_2 = models.IntegerField(null=True, blank=True)

    # Ehm Ftple Delhi Twelve
    Full_Power_Run_Ex_Gas_Temp_M_GT_3 = models.IntegerField(null=True, blank=True)
    Full_Power_Run_Ex_Gas_Temp_M_GT_4 = models.IntegerField(null=True, blank=True)
    Full_Power_Run_Slip_Exh_Gas_Temp_GT_3 = models.IntegerField(null=True, blank=True)
    Full_Power_Run_Slip_Exh_Gas_Temp_GT_4 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Thirteen
    Full_Astern_Run_Ex_Gas_Temp_M_GT_1 = models.IntegerField(null=True, blank=True)
    Full_Astern_Run_Ex_Gas_Temp_M_GT_2 = models.IntegerField(null=True, blank=True)
    Full_Astern_Run_Slip_Exh_Gas_Temp_GT_1 = models.IntegerField(null=True, blank=True)
    Full_Astern_Run_Slip_Exh_Gas_Temp_GT_2 = models.IntegerField(null=True, blank=True)
    # Ehm Ftple Delhi Fourteen:
    Full_Astern_Run_Ex_Gas_Temp_M_GT_3 = models.IntegerField(null=True, blank=True)
    Full_Astern_Run_Ex_Gas_Temp_M_GT_4 = models.IntegerField(null=True, blank=True)
    Full_Astern_Run_Slip_Exh_Gas_Temp_GT_3 = models.IntegerField(null=True, blank=True)
    Full_Astern_Run_Slip_Exh_Gas_Temp_GT_4 = models.IntegerField(null=True, blank=True)

    def _str_(self):
        return self.name

    class Meta:
        db_table = "GtttDelhiTempChart"
        verbose_name = "GtttDelhiTempChart"
        verbose_name_plural = "GtttDelhiTempChart"


class TempImportData(models.Model):
    # running_id = models.ForeignKey(TempImport, on_delete=models.CASCADE,null=True)
    trial_unit = models.TextField(null=True, blank=True)
    satellite_unit = models.CharField(max_length=150, blank=True, null=True)
    ship = models.CharField(max_length=150, blank=True, null=True)
    section = models.CharField(max_length=150, blank=True, null=True)
    equipment = models.CharField(max_length=150, blank=True, null=True)
    boilers = models.CharField(max_length=150, blank=True, null=True)
    trial_date = models.CharField(max_length=150, blank=True, null=True)
    trial_type = models.TextField(blank=True, null=True)

    def _str_(self):
        return self.name

    class Meta:
        db_table = "TempImport"
        verbose_name = "TempImport"
        verbose_name_plural = "TempImport"


# Approval of trials
class trialStatus(models.Model):
    trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)
    process_flow = models.ForeignKey(ProcessFlow, on_delete=models.CASCADE, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(null=True)


class trialApproval(models.Model):
    trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)
    comments = models.TextField(null=True, blank=True)
    type = models.SmallIntegerField(
        choices=((1, "Recommendation"), (2, "Approval")), null=True, blank=True
    )
    status = models.SmallIntegerField(
        choices=((1, "Approved"), (2, "Rejected")), null=True, blank=True
    )
    approved_role = models.ForeignKey(
        AccessUserRoles, on_delete=models.CASCADE, null=True
    )
    approved_level = models.SmallIntegerField(null=True)
    approved_on = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    approved_ip = models.GenericIPAddressField(null=True)


# 1
class HSconvertor(models.Model):
    trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)
    occation_of_trial = models.TextField(null=True, blank=True)
    trial_date = models.DateField(blank=True, null=True)
    trial_conv_no = models.TextField(null=True, blank=True)
    shipID = models.CharField(max_length=150, blank=True, null=True)
    trial_code = models.TextField(null=True, blank=True)
    equipmentCode = models.CharField(max_length=150, blank=True, null=True)
    occationOfCurrTrial = models.TextField(null=True, blank=True)
    lastTrialDate = models.DateField(blank=True, null=True)
    referanceTrialID = models.CharField(max_length=150, blank=True, null=True)
    referanceFileID = models.CharField(max_length=150, blank=True, null=True)
    referanceDocID = models.CharField(max_length=150, blank=True, null=True)
    testEquipmentUsed = models.TextField(null=True, blank=True)
    motr_equipmentID = models.TextField(null=True, blank=True)
    motr_equipmentSrNo = models.TextField(null=True, blank=True)
    motr_rpm_val = models.TextField(null=True, blank=True)
    motr_bearingNo = models.TextField(null=True, blank=True)
    motr_inpSupply = models.TextField(null=True, blank=True)
    altnr_equipmentID = models.TextField(null=True, blank=True)
    altnr_equipmentSrNo = models.TextField(null=True, blank=True)
    altnr_RatedVoltage = models.TextField(null=True, blank=True)
    altnr_RatedFrequency = models.TextField(null=True, blank=True)
    altnr_RatedVal = models.TextField(null=True, blank=True)
    altnr_RatedCurrentVal = models.TextField(null=True, blank=True)
    altnr_BearingNo = models.TextField(null=True, blank=True)
    avr_equipmentID = models.TextField(null=True, blank=True)
    avr_equipmentSrNo = models.TextField(null=True, blank=True)
    ir_alternator = models.TextField(null=True, blank=True)
    ir_motor = models.TextField(null=True, blank=True)
    proChck_OVP_CDate = models.DateField(blank=True, null=True)
    proChck_OVP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_OVP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_OVP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_OVP_Remarks = models.TextField(null=True, blank=True)
    proChck_OLP_CDate = models.DateField(blank=True, null=True)
    proChck_OLP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_OLP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_OLP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_OLP_Remarks = models.TextField(null=True, blank=True)
    proChck_SPP_CDate = models.DateField(blank=True, null=True)
    proChck_SPP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_SPP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_SPP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_SPP_Remarks = models.TextField(null=True, blank=True)
    proChck_WTP_CDate = models.DateField(blank=True, null=True)
    proChck_WTP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_WTP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_WTP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_WTP_Remarks = models.TextField(null=True, blank=True)
    instrmtn_VM_ops = models.CharField(max_length=150, null=True, blank=True)
    instrmtn_VM_CDate = models.DateField(blank=True, null=True)
    instrmtn_VM_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    instrmtn_VM_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    instrmtn_VM_Remarks = models.TextField(null=True, blank=True)
    instrmtn_FM_ops = models.CharField(max_length=150, null=True, blank=True)
    instrmtn_FM_CDate = models.DateField(blank=True, null=True)
    instrmtn_FM_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    instrmtn_FM_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    instrmtn_FM_Remarks = models.TextField(null=True, blank=True)
    instrmtn_AMM_ops = models.CharField(max_length=150, null=True, blank=True)
    instrmtn_AMM_CDate = models.DateField(blank=True, null=True)
    instrmtn_AMM_CertSts = models.CharField(max_length=25,choices=(('Yes','Yes'),('No','No')),blank=True,null=True)
    instrmtn_AMM_Sts = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    instrmtn_AMM_Remarks = models.TextField(null=True,blank=True)
    motrHlthCh_SPM = models.TextField(null=True,blank=True)
    motrHlthCh_StrtCurnt = models.TextField(null=True,blank=True)
    motrHlthCh_RunCurnt = models.TextField(null=True,blank=True)
    motrHlthCh_PhseBal = models.TextField(null=True,blank=True)
    altnrHlthCh_SPM = models.TextField(null=True,blank=True)
    altnrHlthCh_RstnsOfWind = models.TextField(null=True,blank=True)
    altnrHlthCh_InductncOfWind = models.TextField(null=True,blank=True)
    misc_past_Eqpt_hst = models.TextField(null=True,blank=True)
    misc_past_Eqpt_hst_remarks = models.TextField(null=True,blank=True)
    misc_lighting = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_lighting_remarks = models.TextField(null=True,blank=True)
    misc_cooling = models.CharField(max_length=25,choices=(('Natural Air','Natural Air'),('Forced Cooling','Forced Cooling')),null=True,blank=True)
    misc_cooling_remarks = models.TextField(null=True,blank=True)
    misc_earthing = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_earthing_remarks = models.TextField(null=True,blank=True)
    misc_cbl_cond = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_cbl_cond_remarks = models.TextField(null=True,blank=True)
    misc_cleanliness = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_cleanliness_remarks = models.TextField(null=True,blank=True)
    misc_indication = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_indication_remarks = models.TextField(null=True,blank=True)
    misc_Eqpt = models.TextField(null=True,blank=True)
    misc_Eqpt_remarks = models.TextField(null=True,blank=True)
    voltRegln_Nlod_AVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_AVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_HVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_HVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_permsble_volt = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_remarks = models.TextField(null=True,blank=True)
    voltRegln_Flod_AVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_AVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_HVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_HVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_permsble_volt = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_remarks = models.TextField(null=True,blank=True)
    voltBalTst_Nlod_VO_RY = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Nlod_VO_YB = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Nlod_VO_BR = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Nlod_dif_val = models.TextField(null=True,blank=True)
    voltBalTst_Nlod_remarks = models.TextField(null=True,blank=True)
    voltBalTst_Flod_VO_RY = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Flod_VO_YB = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Flod_VO_BR = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Flod_dif_val = models.TextField(null=True,blank=True)
    voltBalTst_Flod_remarks = models.TextField(null=True,blank=True)
    sstv_100_val = models.TextField(null=True,blank=True)
    sstv_100_ObsVolt = models.TextField(null=True,blank=True)
    sstv_100_PF = models.TextField(null=True,blank=True)
    sstv_100_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_75_val = models.TextField(null=True,blank=True)
    sstv_75_ObsVolt = models.TextField(null=True,blank=True)
    sstv_75_PF = models.TextField(null=True,blank=True)
    sstv_75_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_50_val = models.TextField(null=True,blank=True)
    sstv_50_ObsVolt = models.TextField(null=True,blank=True)
    sstv_50_PF = models.TextField(null=True,blank=True)
    sstv_50_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_25_val = models.TextField(null=True,blank=True)
    sstv_25_ObsVolt = models.TextField(null=True,blank=True)
    sstv_25_PF = models.TextField(null=True,blank=True)
    sstv_25_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_0_val = models.TextField(null=True,blank=True)
    sstv_0_ObsVolt = models.TextField(null=True,blank=True)
    sstv_0_PF = models.TextField(null=True,blank=True)
    sstv_0_Volt_Modln = models.TextField(null=True,blank=True)
    freq_100_val = models.TextField(null=True,blank=True)
    freq_100_ObsVolt = models.TextField(null=True,blank=True)
    freq_100_freq_Modln = models.TextField(null=True,blank=True)
    freq_75_val = models.TextField(null=True,blank=True)
    freq_75_ObsVolt = models.TextField(null=True,blank=True)
    freq_75_freq_Modln = models.TextField(null=True,blank=True)
    freq_50_val = models.TextField(null=True,blank=True)
    freq_50_ObsVolt = models.TextField(null=True,blank=True)
    freq_50_freq_Modln = models.TextField(null=True,blank=True)
    freq_25_val = models.TextField(null=True,blank=True)
    freq_25_ObsVolt = models.TextField(null=True,blank=True)
    freq_25_freq_Modln = models.TextField(null=True,blank=True)
    freq_0_val = models.TextField(null=True,blank=True)
    freq_0_ObsVolt = models.TextField(null=True,blank=True)
    freq_0_freq_Modln = models.TextField(null=True,blank=True)
    vtrt_100x75_int_val = models.TextField(null=True,blank=True)
    vtrt_100x75_memtry_val = models.TextField(null=True,blank=True)
    vtrt_100x75_fnl_val = models.TextField(null=True,blank=True)
    vtrt_100x75_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_100x75_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_75x50_int_val = models.TextField(null=True,blank=True)
    vtrt_75x50_memtry_val = models.TextField(null=True,blank=True)
    vtrt_75x50_fnl_val = models.TextField(null=True,blank=True)
    vtrt_75x50_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_75x50_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_50x25_int_val = models.TextField(null=True,blank=True)
    vtrt_50x25_memtry_val = models.TextField(null=True,blank=True)
    vtrt_50x25_fnl_val = models.TextField(null=True,blank=True)
    vtrt_50x25_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_50x25_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_25x0_int_val = models.TextField(null=True,blank=True)
    vtrt_25x0_memtry_val = models.TextField(null=True,blank=True)
    vtrt_25x0_fnl_val = models.TextField(null=True,blank=True)
    vtrt_25x0_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_25x0_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_0M_int_val = models.TextField(null=True,blank=True)
    vtrt_0M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_0M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_0M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_0M_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_25M_int_val = models.TextField(null=True,blank=True)
    vtrt_25M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_25M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_25M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_25M_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_50M_int_val = models.TextField(null=True,blank=True)
    vtrt_50M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_50M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_50M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_50M_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_94M_int_val = models.TextField(null=True,blank=True)
    vtrt_94M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_94M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_94M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_94M_recov_Obs = models.TextField(null=True,blank=True)
    wavHorCont_max = models.TextField(null=True,blank=True)
    recommendations = models.TextField(null=True,blank=True)

# # 1log
class HSconvertorLog(models.Model):
    running_id = models.ForeignKey(HSconvertor, on_delete=models.CASCADE, null=True)
    trial = models.ForeignKey(Trials, on_delete=models.CASCADE, null=True)
    occation_of_trial = models.TextField(null=True, blank=True)
    trial_date = models.DateField(blank=True, null=True)
    trial_conv_no = models.TextField(null=True, blank=True)
    shipID = models.CharField(max_length=150, blank=True, null=True)
    trial_code = models.TextField(null=True, blank=True)
    equipmentCode = models.CharField(max_length=150, blank=True, null=True)
    occationOfCurrTrial = models.TextField(null=True, blank=True)
    lastTrialDate = models.DateField(blank=True, null=True)
    referanceTrialID = models.CharField(max_length=150, blank=True, null=True)
    referanceFileID = models.CharField(max_length=150, blank=True, null=True)
    referanceDocID = models.CharField(max_length=150, blank=True, null=True)
    testEquipmentUsed = models.TextField(null=True, blank=True)
    motr_equipmentID = models.TextField(null=True, blank=True)
    motr_equipmentSrNo = models.TextField(null=True, blank=True)
    motr_rpm_val = models.TextField(null=True, blank=True)
    motr_bearingNo = models.TextField(null=True, blank=True)
    motr_inpSupply = models.TextField(null=True, blank=True)
    altnr_equipmentID = models.TextField(null=True, blank=True)
    altnr_equipmentSrNo = models.TextField(null=True, blank=True)
    altnr_RatedVoltage = models.TextField(null=True, blank=True)
    altnr_RatedFrequency = models.TextField(null=True, blank=True)
    altnr_RatedVal = models.TextField(null=True, blank=True)
    altnr_RatedCurrentVal = models.TextField(null=True, blank=True)
    altnr_BearingNo = models.TextField(null=True, blank=True)
    avr_equipmentID = models.TextField(null=True, blank=True)
    avr_equipmentSrNo = models.TextField(null=True, blank=True)
    ir_alternator = models.TextField(null=True, blank=True)
    ir_motor = models.TextField(null=True, blank=True)
    proChck_OVP_CDate = models.DateField(blank=True, null=True)
    proChck_OVP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_OVP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_OVP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_OVP_Remarks = models.TextField(null=True, blank=True)
    proChck_OLP_CDate = models.DateField(blank=True, null=True)
    proChck_OLP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_OLP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_OLP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_OLP_Remarks = models.TextField(null=True, blank=True)
    proChck_SPP_CDate = models.DateField(blank=True, null=True)
    proChck_SPP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_SPP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_SPP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_SPP_Remarks = models.TextField(null=True, blank=True)
    proChck_WTP_CDate = models.DateField(blank=True, null=True)
    proChck_WTP_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    proChck_WTP_ObsVal = models.CharField(max_length=150, blank=True, null=True)
    proChck_WTP_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    proChck_WTP_Remarks = models.TextField(null=True, blank=True)
    instrmtn_VM_ops = models.CharField(max_length=150, null=True, blank=True)
    instrmtn_VM_CDate = models.DateField(blank=True, null=True)
    instrmtn_VM_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    instrmtn_VM_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    instrmtn_VM_Remarks = models.TextField(null=True, blank=True)
    instrmtn_FM_ops = models.CharField(max_length=150, null=True, blank=True)
    instrmtn_FM_CDate = models.DateField(blank=True, null=True)
    instrmtn_FM_CertSts = models.CharField(
        max_length=25, choices=(("Yes", "Yes"), ("No", "No")), blank=True, null=True
    )
    instrmtn_FM_Sts = models.CharField(
        max_length=25,
        choices=(("Sat", "Sat"), ("Unsat", "Unsat")),
        null=True,
        blank=True,
    )
    instrmtn_FM_Remarks = models.TextField(null=True, blank=True)
    instrmtn_AMM_ops = models.CharField(max_length=150, null=True, blank=True)
    instrmtn_AMM_CDate = models.DateField(blank=True, null=True)
    instrmtn_AMM_CertSts = models.CharField(max_length=25,choices=(('Yes','Yes'),('No','No')),blank=True,null=True)
    instrmtn_AMM_Sts = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    instrmtn_AMM_Remarks = models.TextField(null=True,blank=True)
    motrHlthCh_SPM = models.TextField(null=True,blank=True)
    motrHlthCh_StrtCurnt = models.TextField(null=True,blank=True)
    motrHlthCh_RunCurnt = models.TextField(null=True,blank=True)
    motrHlthCh_PhseBal = models.TextField(null=True,blank=True)
    altnrHlthCh_SPM = models.TextField(null=True,blank=True)
    altnrHlthCh_RstnsOfWind = models.TextField(null=True,blank=True)
    altnrHlthCh_InductncOfWind = models.TextField(null=True,blank=True)
    misc_past_Eqpt_hst = models.TextField(null=True,blank=True)
    misc_past_Eqpt_hst_remarks = models.TextField(null=True,blank=True)
    misc_lighting = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_lighting_remarks = models.TextField(null=True,blank=True)
    misc_cooling = models.CharField(max_length=25,choices=(('Natural Air','Natural Air'),('Forced Cooling','Forced Cooling')),null=True,blank=True)
    misc_cooling_remarks = models.TextField(null=True,blank=True)
    misc_earthing = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_earthing_remarks = models.TextField(null=True,blank=True)
    misc_cbl_cond = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_cbl_cond_remarks = models.TextField(null=True,blank=True)
    misc_cleanliness = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_cleanliness_remarks = models.TextField(null=True,blank=True)
    misc_indication = models.CharField(max_length=25,choices=(('Sat','Sat'),('Unsat','Unsat')),null=True,blank=True)
    misc_indication_remarks = models.TextField(null=True,blank=True)
    misc_Eqpt = models.TextField(null=True,blank=True)
    misc_Eqpt_remarks = models.TextField(null=True,blank=True)
    voltRegln_Nlod_AVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_AVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_HVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_HVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_permsble_volt = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Nlod_remarks = models.TextField(null=True,blank=True)
    voltRegln_Flod_AVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_AVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_HVR_min = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_HVR_max = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_permsble_volt = models.CharField(max_length=150, null=True,blank=True)
    voltRegln_Flod_remarks = models.TextField(null=True,blank=True)
    voltBalTst_Nlod_VO_RY = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Nlod_VO_YB = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Nlod_VO_BR = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Nlod_dif_val = models.TextField(null=True,blank=True)
    voltBalTst_Nlod_remarks = models.TextField(null=True,blank=True)
    voltBalTst_Flod_VO_RY = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Flod_VO_YB = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Flod_VO_BR = models.CharField(max_length=150, null=True,blank=True)
    voltBalTst_Flod_dif_val = models.TextField(null=True,blank=True)
    voltBalTst_Flod_remarks = models.TextField(null=True,blank=True)
    sstv_100_val = models.TextField(null=True,blank=True)
    sstv_100_ObsVolt = models.TextField(null=True,blank=True)
    sstv_100_PF = models.TextField(null=True,blank=True)
    sstv_100_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_75_val = models.TextField(null=True,blank=True)
    sstv_75_ObsVolt = models.TextField(null=True,blank=True)
    sstv_75_PF = models.TextField(null=True,blank=True)
    sstv_75_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_50_val = models.TextField(null=True,blank=True)
    sstv_50_ObsVolt = models.TextField(null=True,blank=True)
    sstv_50_PF = models.TextField(null=True,blank=True)
    sstv_50_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_25_val = models.TextField(null=True,blank=True)
    sstv_25_ObsVolt = models.TextField(null=True,blank=True)
    sstv_25_PF = models.TextField(null=True,blank=True)
    sstv_25_Volt_Modln = models.TextField(null=True,blank=True)
    sstv_0_val = models.TextField(null=True,blank=True)
    sstv_0_ObsVolt = models.TextField(null=True,blank=True)
    sstv_0_PF = models.TextField(null=True,blank=True)
    sstv_0_Volt_Modln = models.TextField(null=True,blank=True)
    freq_100_val = models.TextField(null=True,blank=True)
    freq_100_ObsVolt = models.TextField(null=True,blank=True)
    freq_100_freq_Modln = models.TextField(null=True,blank=True)
    freq_75_val = models.TextField(null=True,blank=True)
    freq_75_ObsVolt = models.TextField(null=True,blank=True)
    freq_75_freq_Modln = models.TextField(null=True,blank=True)
    freq_50_val = models.TextField(null=True,blank=True)
    freq_50_ObsVolt = models.TextField(null=True,blank=True)
    freq_50_freq_Modln = models.TextField(null=True,blank=True)
    freq_25_val = models.TextField(null=True,blank=True)
    freq_25_ObsVolt = models.TextField(null=True,blank=True)
    freq_25_freq_Modln = models.TextField(null=True,blank=True)
    freq_0_val = models.TextField(null=True,blank=True)
    freq_0_ObsVolt = models.TextField(null=True,blank=True)
    freq_0_freq_Modln = models.TextField(null=True,blank=True)
    vtrt_100x75_int_val = models.TextField(null=True,blank=True)
    vtrt_100x75_memtry_val = models.TextField(null=True,blank=True)
    vtrt_100x75_fnl_val = models.TextField(null=True,blank=True)
    vtrt_100x75_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_100x75_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_75x50_int_val = models.TextField(null=True,blank=True)
    vtrt_75x50_memtry_val = models.TextField(null=True,blank=True)
    vtrt_75x50_fnl_val = models.TextField(null=True,blank=True)
    vtrt_75x50_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_75x50_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_50x25_int_val = models.TextField(null=True,blank=True)
    vtrt_50x25_memtry_val = models.TextField(null=True,blank=True)
    vtrt_50x25_fnl_val = models.TextField(null=True,blank=True)
    vtrt_50x25_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_50x25_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_25x0_int_val = models.TextField(null=True,blank=True)
    vtrt_25x0_memtry_val = models.TextField(null=True,blank=True)
    vtrt_25x0_fnl_val = models.TextField(null=True,blank=True)
    vtrt_25x0_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_25x0_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_0M_int_val = models.TextField(null=True,blank=True)
    vtrt_0M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_0M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_0M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_0M_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_25M_int_val = models.TextField(null=True,blank=True)
    vtrt_25M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_25M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_25M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_25M_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_50M_int_val = models.TextField(null=True,blank=True)
    vtrt_50M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_50M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_50M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_50M_recov_Obs = models.TextField(null=True,blank=True)
    vtrt_94M_int_val = models.TextField(null=True,blank=True)
    vtrt_94M_memtry_val = models.TextField(null=True,blank=True)
    vtrt_94M_fnl_val = models.TextField(null=True,blank=True)
    vtrt_94M_varn_Obs = models.TextField(null=True,blank=True)
    vtrt_94M_recov_Obs = models.TextField(null=True,blank=True)
    wavHorCont_max = models.TextField(null=True,blank=True)
    recommendations = models.TextField(null=True,blank=True)

    def _str_(self):
        return self.name

    class Meta:
        db_table = "log.HSconvertor"
        verbose_name = "HSconvertor"
        verbose_name_plural = "HSconvertor"
