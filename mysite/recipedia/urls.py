from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.find_and_parse_recipes2, name='search'),
    path('search2', views.find_and_parse_recipes, name='search2')
]