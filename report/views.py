from django.contrib.auth.models import User
from report.models import Report, Reaction, Report_Image
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files import File

from learn.views import *

@api_view(['POST'])
@parser_classes([MultiPartParser])
def createReport(request):
    usr = request.POST['user']
    desc = request.POST['description']
    fl = request.POST['floodLevel']
    lat = request.POST['latitude']
    long = request.POST['longitude']

    r = Report(user = User.objects.get(id = usr),
    description = desc, 
    floodLevel = fl,
    latitude = lat,
    longitude = long)
    r.save()

    # location = Location(lat, long)
    # if save_area(location, fl) is False:
    #     return Response("Fail")
    
    print(request.FILES.getlist('ReportImages'))

    if request.FILES.get('ReportImages') is not None:
        for image in request.FILES.getlist('ReportImages'):
            file = File(image)
            Report_Image(image = File(image), report = r).save()

    return Response("Success")

@api_view(['POST'])
def create_report(request):
    print('was here!')
    usr = request.data.get('user')
    desc = request.data.get('description')
    fl = request.data.get('floodLevel')
    lat = request.data.get('latitude')
    long = request.data.get('longitude')

    r = Report(user = User.objects.get(id = usr),
            description = desc, 
            floodLevel = fl,
            latitude = lat,
            longitude = long)
    r.save()

    resp = 'none'
    location = Location(float(lat), float(long))
    if save_area(location, fl) is False:
        resp = 'location is present in the prone area database'
    else:
        resp = 'location successfully added as prone area'
    return Response({'response':resp})

@api_view(['POST'])
def reactToReport(request):
    report = Report.objects.get(id = request.data['report'])
    user = User.objects.get(id = request.data['user'])
    isPositive = request.data['isPositive']

    Reaction(report=report,user=user,isPositive=isPositive).save()

    return Response(request.data)