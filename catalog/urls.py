from django.urls import path
from . import views

urlpatterns = [

]


# The home page address is added here
urlpatterns += [
    path('', views.index, name='index'),
]