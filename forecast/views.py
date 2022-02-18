from django.db.models import query
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import permission_classes

import requests
import json

from django.contrib.auth.models import User
from .models import FloodProneArea, FloodLevel
from report.models import Report, Report_Image, Reaction
from .serializers import FloodProneAreaSerializer, FloodLevelSerializer
from .serializers import ReportSerializer, ReportImageSerializer, ReactionSerializer
from learn.views import distance, Location

class FloodProneAreaViewSet(viewsets.ModelViewSet):
    serializer_class = FloodProneAreaSerializer
    
    def get_queryset(self):
        queryset = FloodProneArea.objects.all()
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        # optimization: filter the objects that X away from the location first
        if latitude is not None and longitude is not None:
            latitude = float(latitude)
            longitude = float(longitude)
            location = Location(latitude,longitude)
            ids = []
            for qs in queryset:
                lat = qs.latitude
                long = qs.longitude
                loc = Location(lat,long)
                d = distance(location,loc)
                if d<=500:
                    ids.append(qs.id)
            queryset = queryset.filter(id__in=ids)
        return queryset

class FloodLevelViewSet(viewsets.ModelViewSet):
    queryset = FloodLevel.objects.all()
    serializer_class = FloodLevelSerializer
    permission_classes = [permissions.IsAuthenticated]

@permission_classes([permissions.IsAuthenticated])
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        queryset = Report.objects.all().order_by('timestamp')
        area_id = self.request.query_params.get('area_id')
        # optimization: filter the objects that X away from the location first
        if area_id is not None:
            area_id = int(area_id)
            queryset = queryset.filter(area__id=area_id)
        return queryset
    
class ReportImageViewSet(viewsets.ModelViewSet):
    serializer_class = ReportImageSerializer

    def get_queryset(self):
        queryset = Report_Image.objects.all()
        report_id = self.request.query_params.get('report_id')
        if report_id is not None:
            report_id = int(report_id)
            report = Report.objects.get(id=report_id)
            queryset = queryset.filter(report=report)
        return queryset

class ReactionViewSet(viewsets.ModelViewSet):
    serializer_class = ReactionSerializer

    def get_queryset(self):
        queryset = Reaction.objects.all()
        report_id = self.request.query_params.get('report_id')
        user_id = self.request.query_params.get('user_id')
        if report_id is not None and user_id is not None:
            report_id = int(report_id)
            user_id = int(user_id)
            report = Report.objects.get(id=report_id)
            user = User.objects.get(id=user_id)
            queryset = queryset.filter(report=report,user=user)
        return queryset