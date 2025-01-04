from django.contrib import admin

from .models import ParkingSpot, ParkingOwner

# Register your models here
admin.site.register(ParkingSpot)
admin.site.register(ParkingOwner)