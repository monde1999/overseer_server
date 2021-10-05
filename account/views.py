from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework import viewsets
from .serializers import UserSerializer

from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.authtoken.models import Token

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

@api_view(["POST"])
def signup(request):
    usr = request.data.get('username')
    pw = request.data.get('password')
    fname = request.data.get('firstName')
    lname = request.data.get('lastName')
    # em = request.data.get('email')

    print(request.data)
    isEmailUnique = False
    new_user = None
    id = -1
    token_key=''
    if usr != '' and pw != '': # validation here
        isExisting = User.objects.filter(username=usr).exists()
        if not isExisting:
            new_user = User(username=usr,email=usr,first_name=fname, last_name=lname)
            isEmailUnique = True
        if new_user is not None:
            new_user.set_password(pw)
            new_user.save()
            id = new_user.id
            token:Token = Token.objects.create(user=new_user)
            token_key = token.key
    
    context = {
        'isEmailUnique':isEmailUnique,
        'token': token_key,
        'id' : id
    }

    return Response(context)


@api_view(["POST"])
def login(request):
    token_key = ''
    username = request.data.get("username")
    password = request.data.get("password")
    f = authenticate(request, username=username, password=password)
    isUserNameCorrect = False
    isPasswordCorrect = False
    firstName = None
    lastName = None
    id = -1   
    if f:   
        user = User.objects.get(username = username)   
        flag = 'true'
        token_key = Token.objects.get_or_create(user=f)[0].key
        username = user.username
        firstName = user.first_name
        lastName = user.last_name
        id = user.id
        isUserNameCorrect = True
        isPasswordCorrect = True
    else:
        isExisting = User.objects.filter(username=username).exists()
        if isExisting:
            isUserNameCorrect = True
        else:
            isUserNameCorrect = False
        username=None
    content = {
        'isUserNameCorrect': isUserNameCorrect,
        'isPasswordCorrect' : isPasswordCorrect,
        'token':token_key,
        'username' : username,
        'firstName' : firstName,
        'lastName' : lastName,
        'id' :id,
    }
    return Response(content)
    