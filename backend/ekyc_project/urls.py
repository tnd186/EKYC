from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the eKYC project!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ekyc_app.urls')),  
    path('', home),  
]