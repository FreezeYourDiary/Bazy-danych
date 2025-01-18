from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/available-parking-spots-with-filters/<int:site_id>/', views.available_parking_spots_with_filters,
         name='available_parking_spots_with_filters'),
    path('api/search-parking/', views.search_parking, name='search_parking'),
    path('api/autocomplete-sites/', views.autocomplete_sites, name='autocomplete_sites'),

    path('api/parking/<int:site_id>/update_details/', views.update_parking_details, name='update_parking_details'),
    path('api/parking/<int:site_id>/update_owner/', views.update_parking_owner, name='update_parking_owner'),
    path('api/parking/<int:parking_id>/update_price/', views.update_parking_price, name='update_parking_price'),
    path('api/reservations/', views.reservations, name='reservations'),
    path('api/earnings/statistics/', views.earnings_statistics, name='earnings_statistics'),
    path('api/user/<int:user_id>/statistics/', views.user_statistics, name='user_statistics'),

    path('signup/', views.signup_page, name='signup_page'),
    path('signup-action/', views.signup, name='signup'),  # test

    path('login/', views.login_page, name='signup_page'),
    path('api/login/', views.login_user, name='login_user'),
    path('is_logged_in/', views.is_logged_in, name='is_logged_in'),

    path('konto/', views.konto_page, name='konto_page'),
    path('logout/', views.logout, name='logout'),

]
