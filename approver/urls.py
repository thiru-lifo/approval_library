from django.urls import path
from . import views

urlpatterns = [
    path("config", views.ConfigCRUD.as_view(), name="Config CURD"),
    path("config_list", views.ConfigList.as_view(), name="Config List"),
]
