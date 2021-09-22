from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('account/', include('account.urls'), name='account'),
    path('forecast/', include('forecast.urls'), name='forecast'),
    path('report/', include('report.urls'), name='report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
