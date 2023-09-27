from django.urls import path
from . import views

urlpatterns = [
    path("config", views.ConfigCRUD.as_view(), name="Config CURD"),
    path("config_list", views.ConfigList.as_view(), name="Config List"),
    path(
        "approved_config",
        views.ApprovedConfigCRUD.as_view(),
        name="Approved Config CURD",
    ),
    path(
        "approved_config_list",
        views.ApprovedConfigList.as_view(),
        name="Approved Config List",
    ),
    path(
        "get_approved_config",
        views.GetApprovedDetails.as_view(),
        name="Get Approved Config Details",
    ),
    path("approval_status", views.ApprovalStatus.as_view(), name="Approved Status"),
    path(
        "approval_status_list",
        views.ApprovalStatusList.as_view(),
        name="Approved Status List",
    ),
    path(
        "approval_history",
        views.ApprovalHistory.as_view(),
        name="Approval History",
    ),
]
