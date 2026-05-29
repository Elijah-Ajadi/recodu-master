from django.urls import path
from . import views

app_name = "vitals"

urlpatterns = [
    path("create/", views.create, name="create"),
    path("<int:pk>/edit/", views.edit, name="edit"),
    path("<int:pk>/request-correction/", views.request_correction, name="request_correction"),
]
