"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from mysite.view import hello,current_datetime,hours_ahead,test_model,index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/',hello),
    path('time/', current_datetime),
    re_path(r'^time/plus/(\d{1,2})/$',hours_ahead),
    path('test_model/', test_model),
    re_path(r'^$',index),
]
