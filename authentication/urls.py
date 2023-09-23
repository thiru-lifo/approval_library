from django.urls import path
from . import views
from django.contrib import admin

# from django.conf.urls import url
from django.urls import re_path as url


admin.autodiscover()
urlpatterns = [
    path("token", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout", views.LogoutView.as_view(), name="logout_api"),
    path("authentications", views.authenticationView.as_view(), name="logout_api"),
    path("resend-code", views.ResendCodeView.as_view(), name="logout_api"),
    # path('token/refresh', views.MyTokenRefreshView.as_view(), name= 'refreshtoken'),
    path(
        "verifyemailverificationcode",
        views.CorrectVerificationCode.as_view(),
        name="verifyemailverificationcode",
    ),
    path("change-password", views.ChangePasswordAPI.as_view()),
    path("users", views.userList.as_view(), name="User List"),
    path("users/crud", views.usersCRUD.as_view(), name="User CRUD"),
    path("users/import_excel", views.userImport.as_view(), name="User Import"),
    path("adcheck", views.adcheck, name="adcheck"),
    path("attrs", views.attrs, name="attrs"),
    path("metadata", views.metadata, name="metadata"),
]
