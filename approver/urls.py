from django.urls import path
from . import views

urlpatterns = [
    path("config", views.ConfigCRUD.as_view(), name="Config CURD"),
    path("config_list", views.ConfigList.as_view(), name="Config List"),
    path("approved_config", views.ApprovedConfigCRUD.as_view(), name="Approved Config CURD"),
    path("approved_config_list", views.ApprovedConfigList.as_view(), name="Approved Config List"),
    #path("approval_status", views.ApprovedConfigCRUD.as_view(), name="Approved Status"),
]
