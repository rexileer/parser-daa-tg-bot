from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.index, name='index'),
    path('ad/<str:ad_id>/', views.ad_detail, name='ad_detail'),
] 