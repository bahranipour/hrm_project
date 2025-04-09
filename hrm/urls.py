from django.urls import path
from . import views


urlpatterns = [
    path('', views.my_leave_requests, name='my_leave_requests'),
    path('leave-request/create/',views.create_leave_request,name='create_leave_request'),
    path('leave-request/edit/<int:pk>/', views.edit_leave_request, name='edit_leave_request'),
    path('attendance/check-in/', views.check_in, name='check_in'),
    path('attendance/check-out/', views.check_out, name='check_out'),
    path('attendance/dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    path('my-salary/', views.my_salary, name='my_salary'),
 
]