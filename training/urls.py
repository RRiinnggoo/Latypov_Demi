from django.urls import path

from . import views
 
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/new/', views.request_create, name='request_create'),
    path('requests/<int:request_id>/review/', views.review_create, name='review_create'),
    path('staff/', views.staff_panel, name='staff_panel'),
    path('staff/programs/new/', views.staff_program_create, name='staff_program_create'),
    path('staff/<int:request_id>/state/', views.staff_change_state, name='staff_change_state'),
]
