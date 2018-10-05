from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from analysis import views as analysis_views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/$', analysis_views.Distribution.as_view()),
]
