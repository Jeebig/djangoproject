from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('datetime/', views.current_datetime, name="current_datetime"),
    path('datetime_class/', views.CurrentDateTimeView.as_view(), name="current_datetime_class"),
]
