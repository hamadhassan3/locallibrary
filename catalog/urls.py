from django.urls import path
from . import views

urlpatterns = [

    # The home page address is added here
    path('', views.index, name='index'),

]
