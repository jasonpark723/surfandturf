from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.admin_login),
    url(r'^login$', views.admin_for_login),
    url(r'^dashboard$', views.dashboard),
    # url(r'^dashboard$', views.dashboard),
]
