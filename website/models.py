from django.db import models
from accounts.models import User
from django.db.models.deletion import CASCADE
from master.models import (
    TrialUnits,
)


# Create your models here.
class Pages(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    page_title = models.TextField(default="", blank=True)
    page_content = models.TextField(default="", blank=True)
    page_status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    page_featured_image = models.FileField(upload_to="pages/", blank=True, null=True)
    page_slug = models.CharField(max_length=150, null=True, blank=True, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        db_table = "Pages"

    def __str__(self):
        return str(self.page_title)


class Sliders(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to="slider_image/", blank=True, null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), null=True, blank=True
    )
    slider_link = models.CharField(max_length=150, null=True, blank=True)
    slider_sequence = models.IntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_ip = models.GenericIPAddressField(blank=True, null=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    modified_ip = models.GenericIPAddressField(blank=True, null=True)
    sequence = models.IntegerField(null=True, blank=True, default=1)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Sliders"


# # contact-us
# class Contact(models.Model):
#     name = models.CharField(max_length=100, null=True, blank=True)
#     email = models.EmailField(null=True, blank=True)
#     mobile = models.CharField(max_length=15, null=True, blank=True)
#     created_on = models.DateTimeField(auto_now_add=True, null=True)
#     status = models.SmallIntegerField(
#         choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), default=1
#     )
#     message = models.CharField(max_length=200, null=True, blank=True)


# contact-us
class Contact(models.Model):
    trial_unit = models.ForeignKey(
        TrialUnits, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    status = models.SmallIntegerField(
        choices=((1, "Active"), (2, "Inactive"), (3, "Delete")), default=1
    )
    message = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
