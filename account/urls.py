from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('',include(router.urls), name='user_list'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
]