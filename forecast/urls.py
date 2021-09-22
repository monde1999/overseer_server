from django.db.models import base
from forecast.models import FloodProneArea
from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'flood-prone-areas', views.FloodProneAreaViewSet, basename='forecast')
router.register(r'flood-level', views.FloodLevelViewSet)
router.register(r'reports', views.ReportViewSet, basename='forecast')
router.register(r'report-images', views.ReportImageViewSet, basename='forecast')
router.register(r'report-reactions', views.ReactionViewSet, basename='forecast')

urlpatterns = [
    path('', include(router.urls)),
]