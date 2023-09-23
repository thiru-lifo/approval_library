from django.urls import path
from . import views

urlpatterns = [
    path("trials", views.TrialsList.as_view(), name="Trial Units List"),
    path("intiate-to-rec", views.IntiateToRec.as_view(), name="Intiate To Rec"),
    path("trials/approval", views.TrialsApproval.as_view(), name="Trial Approval"),
    path(
        "trial-approvals",
        views.TrialsApprovalList.as_view(),
        name="Trial Approval List",
    ),
    path("approved_history", views.ApprovalHistory.as_view()),
    # path(
    #     "hs-converter", views.HSConverterList.as_view(), name="Trial HSConverter List"
    # ),
    # path(
    #     "hs-converter/crud",
    #     views.HSConverterCRUD.as_view(),
    #     name="Trial HSConverter CRUD",
    # ),
    # path(
    #     "hs-converter/log",
    #     views.HSConverterlogList.as_view(),
    #     name="Trial HSConverter Log",
    # ),
    # path("hs-converter/report/<trial_id>", views.hs_converter),
]
