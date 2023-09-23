from django.db import models
from accounts.models import User
# Create your models here.


class Config(models.Model):
	name = models.CharField(max_length=150, blank=True, null=True)
	code = models.CharField(max_length=150, blank=True, null=True)
	desc = models.TextField(blank=True, null=True)
	created = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	modified = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="config_modified_id")
	created_ip = models.GenericIPAddressField(null=True)
	modified_ip = models.GenericIPAddressField(blank=True, null=True)
	status = models.SmallIntegerField(choices=((1,'Active'),(2,'Inactive'),(3,'Delete')))
	def _str_(self):
	    return self.name

	class Meta:
	    db_table = "master.config"
	    verbose_name = "Config"
	    verbose_name_plural = "Config"