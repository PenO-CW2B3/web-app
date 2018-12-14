from django.urls import path
from django.conf.urls import url
from mylock import views

app_name = 'mylock'
urlpatterns = [
    path('', views.home, name='home'),
    url(r'^validate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.validate_request, name='validate'),
    url(r'^verificate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.verificate_account, name='verificate'),
    path('users/', views.users, name='users'),
    path('users/add_user/', views.add_user, name='add_user'),
    path('users/add_user/<str:new_user>/setup_fingerprint/', views.setup_fingerprint, name='setup_fingerprint'),
    path('users/add_user/<str:new_user>/setup_facial_recognition/', views.setup_facial_recognition_explanation, name='setup_facial_recognition_explanation'),
    path('users/add_user/<str:new_user>/setup_facial_recognition/<int:photo_number>/', views.setup_facial_recognition, name='setup_facial_recognition'),
    path('users/<str:user>/', views.user_detail, name='user_detail'),
    path('users/<str:user>/delete_user/', views.delete_user, name='delete_user'),
    path('log/', views.log, name='log'),
    path('backup_password/', views.backup_password, name ='backup_password'),
]
