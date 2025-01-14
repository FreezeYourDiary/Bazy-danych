from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('api/available-parking-spots-for-site/<int:site_id>/', views.available_parking_spots_for_site,
         name='available_parking_spots_for_site'),
    path('api/search-parking/', views.search_parking, name='search_parking'),
    path('api/autocomplete-sites/', views.autocomplete_sites, name='autocomplete_sites'),

    # API views for the new functionalities
    path('api/parking/<int:site_id>/update_details/', views.update_parking_details, name='update_parking_details'),
    path('api/parking/<int:site_id>/update_owner/', views.update_parking_owner, name='update_parking_owner'),
    path('api/parking/<int:parking_id>/update_price/', views.update_parking_price, name='update_parking_price'),
    path('api/reservations/', views.reservations, name='reservations'),
    path('api/earnings/statistics/', views.earnings_statistics, name='earnings_statistics'),
    path('api/user/<int:user_id>/statistics/', views.user_statistics, name='user_statistics'),

]
