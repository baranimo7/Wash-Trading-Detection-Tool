from django.urls import path

from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('get-image-as-json/', views.get_image_as_json, name='get-image-as-json'),
]
