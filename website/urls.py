from django.urls import path
from . import views

urlpatterns = [
    # home - Page
    path("pages", views.PagesList.as_view(), name="Pages List"),
    path("pages/crud", views.PagesCRUD.as_view(), name="Pages CRUD"),
    path("sliders", views.SlidersList.as_view(), name="Sliders List"),
    path("sliders/crud", views.SlidersCRUD.as_view(), name="Sliders CRUD"),
    # contact-us
    path("contact", views.ContactViewList.as_view(), name="contact_us list"),
    path("contact/post", views.ContactViewPOST.as_view(), name="contact_us post"),
]
