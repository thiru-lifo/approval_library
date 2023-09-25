from django.db import models
from accounts.models import User
from access.models import AccessUserRoles, ProcessFlow
# Create your models here.


class Config(models.Model):
	name = models.CharField(max_length=150, blank=True, null=True)
	code = models.CharField(max_length=150, blank=True, null=True)
	desc = models.TextField(blank=True, null=True)
	status = models.SmallIntegerField(choices=((1,'Active'),(2,'Inactive'),(3,'Delete')))
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	created_ip = models.GenericIPAddressField(null=True)
	modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	modified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="config_modified_id")
	modified_ip = models.GenericIPAddressField(blank=True, null=True)

	def _str_(self):
	    return self.name

	class Meta:
	    db_table = "master.config"
	    verbose_name = "Config"
	    verbose_name_plural = "Config"


class ApprovedConfig(models.Model):

	config = models.ForeignKey(Config, on_delete= models.CASCADE, null=True)
	role = models.ForeignKey(AccessUserRoles, on_delete=models.CASCADE, null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	type = models.SmallIntegerField(choices=((1,'Recommender'),(2,'Approver')))
	level = models.SmallIntegerField(null=True, blank=True)
	status = models.SmallIntegerField(choices=((1,'Active'),(2,'Inactive'),(3,'Delete')))
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="approver_config_created_by")
	created_ip = models.GenericIPAddressField(null=True)
	modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
	modified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="approver_config_modified_by")
	modified_ip = models.GenericIPAddressField(blank=True, null=True)

	def _str_(self):
	    return self.config

	class Meta:
	    db_table = "master.approved_config"
	    verbose_name = "ApprovedConfig"
	    verbose_name_plural = "ApprovedConfig"