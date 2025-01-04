from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def home(request):
    return HttpResponse("/admin dla admin")

# html test for future

# def home(request):
#     # Fetch all parking spots and owners
#     parking_spots = ParkingSpot.objects.all()
#     parking_owners = ParkingOwner.objects.all()
#
#     # Pass the data to the template
#     context = {
#         'parking_spots': parking_spots,
#         'parking_owners': parking_owners
#     }
#
#     return render(request, 'home.html', context)