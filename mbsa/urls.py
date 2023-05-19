from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from mbsa import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/<object_key>", views.search, name="search"),
    path("status/<object_key>", views.object_page, name="object_page")
] 