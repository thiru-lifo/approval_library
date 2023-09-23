from django.urls import path
from . import views

urlpatterns = [
    path(
        "equipments-graph-data",
        views.EquipmentsGraphData.as_view(),
        name="Equipment Graph Data",
    ),
    path("countries", views.CountriesViews.as_view(), name="viewcountries"),
    path("countries/<int:pk>", views.CountriesViews.as_view(), name="viewcountry"),
    path(
        "countries/details", views.CountriesDetailViews.as_view(), name="addcountries"
    ),
    # count
    path("ship/count", views.ShipCount.as_view(), name="ShipCount"),
    path("section/count", views.SectionCount.as_view(), name="SectionCount"),
    path("equipment/count", views.EquipmentCount.as_view(), name="EquipmentCount"),
    # .....
    path("states", views.StatesViews.as_view(), name="viewstates"),
    path("states/<int:pk>", views.StatesViews.as_view(), name="viewstate"),
    path("states/details", views.StatesDetailViews.as_view(), name="addstates"),
    path("cities", views.CityViews.as_view(), name="viewcities"),
    path("cities/<int:pk>", views.CityViews.as_view(), name="viewcity"),
    path("cities/details", views.CityDetailViews.as_view(), name="addcities"),
    path("lookup_type", views.LookupTypeViews.as_view(), name="view_lookup_type"),
    path(
        "lookup_type/<int:pk>", views.LookupTypeViews.as_view(), name="view_lookup_type"
    ),
    path(
        "lookup_type/details",
        views.LookupTypeDetailViews.as_view(),
        name="add_lookup_type",
    ),
    path("lookup", views.LookupViews.as_view(), name="view_lookup"),
    path("lookup/<int:pk>", views.LookupViews.as_view(), name="view_lookup"),
    path("lookup/details", views.LookupDetailViews.as_view(), name="add_lookup"),
    path("region", views.RegionViews.as_view(), name="view_region"),
    path("region/<int:pk>", views.RegionViews.as_view(), name="view_region"),
    path("region/details", views.RegionDetailViews.as_view(), name="add_region"),
    path("trial_units", views.TrialUnitsList.as_view(), name="Trial Units List"),
    path("trial_units/crud", views.TrialUnitsCRUD.as_view(), name="Trial Units CRUD"),
    path(
        "satellite_units",
        views.SatelliteUnitsList.as_view(),
        name="SatelliteUnits List",
    ),
    path(
        "satellite_units/crud",
        views.SatelliteUnitsCRUD.as_view(),
        name="SatelliteUnits CRUD",
    ),
    path("command", views.CommandList.as_view(), name="Command List"),
    path("command/crud", views.CommandCRUD.as_view(), name="Command CRUD"),
    path("ships", views.ShipsList.as_view(), name="Ships List"),
    path("ships/crud", views.ShipsCRUD.as_view(), name="Ships CRUD"),
    path("sections", views.SectionsList.as_view(), name="Sections List"),
    path("sections/crud", views.SectionsCRUD.as_view(), name="Sections CRUD"),
    path("equipments", views.EquipmentsList.as_view(), name="Equipments List"),
    path("equipments/crud", views.EquipmentsCRUD.as_view(), name="Equipments CRUD"),
    path("boilers", views.BoilersList.as_view(), name="Boilers List"),
    path("boilers_demo", views.BoilersListDemo.as_view(), name="Boilers List"),
    path("boilers/crud", views.BoilersCRUD.as_view(), name="Boilers CRUD"),
    path("trial_types", views.TrialTypesList.as_view(), name="TrialTypes List"),
    path("trial_types/crud", views.TrialTypesCRUD.as_view(), name="TrialTypes CRUD"),
    path("department", views.DepartmentList.as_view(), name="Department List"),
    path("department/crud", views.DepartmentCRUD.as_view(), name="Department CRUD"),
    path("landing", views.LandingList.as_view(), name="Landing List"),
    path("landing/crud", views.landingCRUD.as_view(), name="Landing CRUD"),
    path(
        "equipments-graph-data",
        views.EquipmentsGraphData.as_view(),
        name="Equipment Graph Data",
    ),
]
