from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('api/parking/<int:parking_id>/availability/', views.check_spot_availability, name='spot-availability'),
    path('api/sites/', views.list_sites, name='list_sites'),

    # API views for the new functionalities
    path('api/parking/<int:site_id>/update_details/', views.update_parking_details, name='update_parking_details'),
    path('api/parking/<int:site_id>/update_owner/', views.update_parking_owner, name='update_parking_owner'),
    path('api/parking/<int:parking_id>/update_price/', views.update_parking_price, name='update_parking_price'),
    path('api/reservations/', views.reservations, name='reservations'),
    path('api/earnings/statistics/', views.earnings_statistics, name='earnings_statistics'),
    path('api/user/<int:user_id>/statistics/', views.user_statistics, name='user_statistics'),
]
