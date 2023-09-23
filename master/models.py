from logging import critical
from tabnanny import verbose
from django.db import models
from django.db.models.deletion import CASCADE
import phonenumbers

# from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import User
from access.models import AccessUserRoles

# # Create your models here.


class Countries(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=15)
    phone_code = models.CharField(max_length=100)
    currency = models.CharField(max_length=100)
    sequence = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), default=1
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField()
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.countries"
        verbose_name = "Countries"
        verbose_name_plural = "Countries"


class Region(models.Model):
    country = models.ForeignKey(Countries, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete"))
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField()
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.region"
        verbose_name = "region"
        verbose_name_plural = "region"


class States(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=15)
    country = models.ForeignKey(Countries, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete"))
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField()
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.states"
        verbose_name = "States"
        verbose_name_plural = "States"


class Cities(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=15)
    state = models.ForeignKey(States, on_delete=models.CASCADE)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete"))
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField()
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.cities"
        verbose_name = "Cities"
        verbose_name_plural = "Cities"


class LookupType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete"))
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField()
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.lookup_type"
        verbose_name = "Lookup Type"
        verbose_name_plural = "Lookup Type"


class Lookup(models.Model):
    type = models.ForeignKey(LookupType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=150, null=True, blank=True)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete"))
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    created_ip = models.GenericIPAddressField()
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.lookup"
        verbose_name = "Lookup"
        verbose_name_plural = "Lookup"


class TrialUnits(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.trial_units"
        verbose_name = "trial_unit"
        verbose_name_plural = "trial_units"


class Command(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), blank=True, null=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.command"
        verbose_name = "command"
        verbose_name_plural = "command"


class SatelliteUnits(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    command = models.ForeignKey(
        Command, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.satellite_units"
        verbose_name = "satellite_unit"
        verbose_name_plural = "satellite_units"


class Ships(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    command = models.ForeignKey(
        Command, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.ships"
        verbose_name = "ship"
        verbose_name_plural = "ships"


class ShipSatelliteMapping(models.Model):
    # command = models.ForeignKey(Command, on_delete=models.CASCADE)
    satellite_unit = models.ForeignKey(SatelliteUnits, on_delete=models.CASCADE)
    ship = models.ForeignKey(Ships, on_delete=models.CASCADE)

    def __str__(self):
        return self.ship

    class Meta:
        db_table = "master.ships_satellite_mapping"
        verbose_name = "ships_satellite_mapping"
        verbose_name_plural = "ships_satellite_mappings"


class Sections(models.Model):
    trial_unit = models.ForeignKey(TrialUnits, on_delete=models.CASCADE, null=True)
    command = models.ForeignKey(
        Command, on_delete=models.CASCADE, null=True, blank=True
    )
    satellite_unit = models.ForeignKey(
        SatelliteUnits, on_delete=models.CASCADE, null=True
    )
    ship = models.ForeignKey(Ships, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.sections"
        verbose_name = "section"
        verbose_name_plural = "sections"


class SectionTrialUnitMapping(models.Model):
    trial_unit = models.ForeignKey(TrialUnits, on_delete=models.CASCADE, null=True)
    section_code = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.trial_unit

    class Meta:
        db_table = "master.SectionTrialUnitMapping"
        verbose_name = "SectionTrialUnitMapping"
        verbose_name_plural = "SectionTrialUnitMapping"


class Equipments(models.Model):
    trial_unit = models.ForeignKey(TrialUnits, on_delete=models.CASCADE, null=True)
    command = models.ForeignKey(
        Command, on_delete=models.CASCADE, null=True, blank=True
    )
    satellite_unit = models.ForeignKey(
        SatelliteUnits, on_delete=models.CASCADE, null=True
    )

    ship = models.ForeignKey(Ships, on_delete=models.CASCADE, null=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    EquipmentShipID = models.TextField(null=True, blank=True)
    serial_no = models.TextField(null=True, blank=True)
    model = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15, blank=True, null=True)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.equipments"
        verbose_name = "equipment"
        verbose_name_plural = "equipments"


class Boilers(models.Model):
    trial_unit = models.ForeignKey(TrialUnits, on_delete=models.CASCADE, null=True)
    command = models.ForeignKey(
        Command, on_delete=models.CASCADE, null=True, blank=True
    )
    satellite_unit = models.ForeignKey(
        SatelliteUnits, on_delete=models.CASCADE, null=True
    )
    ship = models.ForeignKey(Ships, on_delete=models.CASCADE, null=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15, blank=True, null=True)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.boilers"
        verbose_name = "boilers"
        verbose_name_plural = "boilers"


class TrialTypes(models.Model):
    trial_unit = models.ForeignKey(TrialUnits, on_delete=models.CASCADE, null=True)
    # satellite_unit = models.ForeignKey(SatelliteUnits, on_delete=models.CASCADE,null=True)
    # ship = models.ForeignKey(Ships, on_delete=models.CASCADE,null=True)
    # section = models.ForeignKey(Sections, on_delete=models.CASCADE,null=True)
    # equipment = models.ForeignKey(Equipments, on_delete=models.CASCADE,null=True)
    # boilers = models.ForeignKey(Boilers, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null=True, blank=True)
    url = models.CharField(max_length=500, null=True, blank=True)
    report_url = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.trial_types"
        verbose_name = "trial_type"
        verbose_name_plural = "trial_types"


class DataAccess(models.Model):
    trial_unit = models.ForeignKey(TrialUnits, on_delete=models.CASCADE, null=True)
    satellite_unit = models.ForeignKey(
        SatelliteUnits, on_delete=models.CASCADE, null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.loginname

    class Meta:
        db_table = "access.data_access"
        verbose_name = "Data Access"
        verbose_name_plural = "Data Access"
        unique_together = ("user", "trial_unit", "satellite_unit")


class DataAccessShip(models.Model):
    data_access = models.ForeignKey(DataAccess, on_delete=models.CASCADE, null=True)
    ship = models.ForeignKey(Ships, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user

    class Meta:
        db_table = "access.data_access_ship"
        verbose_name = "Data Access Ship"
        verbose_name_plural = "Data Access Ships"


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=15)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete"))
    )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.department"
        verbose_name = "department"
        verbose_name_plural = "department"


class Landingpage(models.Model):
    name = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=15, null=True)
    url_type = models.CharField(max_length=15, null=True)
    url_target = models.CharField(max_length=15, null=True)
    url = models.CharField(max_length=500, default="", null=True)
    logo = models.FileField(upload_to="Land/", null=True, blank=True)
    sequence = models.IntegerField(null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete"))
    )
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.landing"
        verbose_name = "landing"
        verbose_name_plural = "landing"


class LandingSatMapping(models.Model):
    Landing = models.ForeignKey(Landingpage, on_delete=models.CASCADE, null=True)
    satellite_unit = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "master.LandingSatMapping"
        verbose_name = "LandingSatMapping"
        verbose_name_plural = "LandingSatMapping"
