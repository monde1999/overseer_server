from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework import viewsets
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

@api_view(["POST"])
def signup(request):
    usr = request.data.get('username')
    pw = request.data.get('password')
    fname = request.data.get('firstname')
    lname = request.data.get('lastname')
    em = request.data.get('email')

    flag = 'false'
    new_user = None
    if usr != '' and pw != '': # validation here
        queryset = User.objects.filter(username=usr)
        if (len(queryset)==0):
            new_user = User(username=usr,email=em,first_name=fname, last_name=lname)
        if new_user is not None:
            new_user.set_password(pw)
            new_user.save()
            flag = 'true'
    
    context = {
        'flag': flag
    }

    return Response(context)


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    f = authenticate(request, username=username, password=password)   
    flag = 'false'
    if f is not None:   
        flag = 'true'
    else:
        queryset = User.objects.filter(username=username)
        if len(queryset) > 0:
            flag = 'wrong_password'
    content = {
        'flag': flag
    }
    return Response(content)
    