from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
    path('plots/<str:filename>/', views.send_plot, name='sendplot'),
]