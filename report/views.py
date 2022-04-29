from django.contrib.auth.models import User
from report.models import Report, Reaction, Report_Image
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from django.core.files import File
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.status import HTTP_400_BAD_REQUEST

from learn.views import *

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser,JSONParser])
def createReport(request):
    usr = request.data.get('user',None)
    desc = request.data.get('description',None)
    fl = request.data.get('floodLevel',None)
    lat = request.data.get('latitude',None)
    long = request.data.get('longitude',None)
    
    is_invalid = False
    response_dict = {}
    if usr is None:
        response_dict['user']=['User must be specified']
        is_invalid = True
    if desc is None:
        response_dict['description']=['Description must be specified']
        is_invalid = True
    if fl is None:
        response_dict['floodLevel']=['Flood Level must be specified']
        is_invalid = True
    if lat is None:
        response_dict['latitude']=['Latitude must be specified']
        is_invalid = True
    if long is None:
        response_dict['longitude']=['Longitude must be specified']
        is_invalid = True
    if is_invalid:
        return Response(response_dict,status=HTTP_400_BAD_REQUEST)
    
    """
        pls test this method with this two lines of code
        everytime you report, the location must be saved in the FloodProneArea table
    """
    location = Location(float(lat), float(long))
    area = save_area(location, fl)

    r = Report(user = User.objects.get(id = usr),
            description = desc, 
            floodLevel = fl,
            area=area)
    
    r.save()
    
    print(request.FILES.getlist('ReportImages'))

    if request.FILES.get('ReportImages') is not None:
        for image in request.FILES.getlist('ReportImages'):
            Report_Image(image = File(image), report = r).save()

    return Response({'response':'success'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    usr = request.data.get('user')
    desc = request.data.get('description')
    fl = request.data.get('floodLevel')
    lat = request.data.get('latitude')
    long = request.data.get('longitude')

    location = Location(float(lat), float(long))
    area = save_area(location, fl)

    r = Report(user = User.objects.get(id = usr),
            description = desc, 
            floodLevel = fl,
            area=area)
    r.save()

    return Response({'response':'success'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactToReport(request):
    report = Report.objects.get(id = request.data['report'])
    user = User.objects.get(id = request.data['user'])
    isPositive = request.data['isPositive']
    reactionExists = Reaction.objects.filter(user = user, report = report).exists()
    if not reactionExists:
        Reaction(report=report,user=user,isPositive=isPositive).save()
    else:
        reactionInDb = Reaction.objects.get(user = user, report = report)
        if isPositive == reactionInDb.isPositive:
            reactionInDb.delete()
        else:
            reactionInDb.isPositive = isPositive
            reactionInDb.save()

    return Response({'response':'success'})