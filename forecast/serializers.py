from django.db.models import fields
from rest_framework import serializers
from forecast.models import FloodProneArea, FloodLevel
from report.models import Report, Report_Image, Reaction

class FloodProneAreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FloodProneArea
        fields = ['id','latitude','longitude','radius']

class FloodLevelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FloodLevel
        fields = '__all__'

class ReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report
        fields = ['id','description','floodLevel','timestamp']

class ReportImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report_Image
        fields = ['image']

class ReactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reaction
        fields = ['isPositive']