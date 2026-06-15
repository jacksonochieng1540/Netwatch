from django.urls import path
from .views import topology_graph
urlpatterns = [path('graph/', topology_graph)]
