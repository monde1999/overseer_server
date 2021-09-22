from django.urls import path
from . import views

app_name='report'
urlpatterns = [
    # path('api-view/',views.apiOverview,name="api_view"),
    # path('create-user/',views.createUser,name="create_user_view"),
    path('create/',views.createReport,name="create_report_view"),
    path('create2/',views.create_report,name='create_report_view_2'),
    path('react/',views.reactToReport,name="react_to_report_view"),
]