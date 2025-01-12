from django.shortcuts import render
from .models import ParkingSpot
from rest_framework.decorators import api_view


@api_view(['POST'])
def update_parking_details(request, site_id):
    """
    Update parking details.
    """
    nazwa = request.data.get('nazwa', None)
    ulica = request.data.get('ulica', None)
    kod_pocztowy = request.data.get('kod_pocztowy', None)
    nr_posesji = request.data.get('nr_posesji', None)

    result = Site.objects.filter(id=site_id).update(
        nazwa=nazwa,
        ulica=ulica,
        kod_pocztowy=kod_pocztowy,
        nr_posesji=nr_posesji
    )

    if result:
        return Response({
            "status": "success",
            "message": f"Zmieniono info o Site ID {site_id}.",
            "updated_rows": result
        })
    else:
        return Response({
            "status": "error",
            "message": f"Nie zmieniono detale parkingu ID {site_id}."
        })


@api_view(['POST'])
def update_parking_owner(request, site_id):
    """
    Update the parking owner.
    """
    new_owner_id = request.data.get('new_owner_id')

    if not new_owner_id:
        return Response({
            "status": "error",
            "message": "Wymagane ID wlasciciela."
        })

    result = Site.objects.filter(id=site_id).update(parking_owner_id=new_owner_id)

    if result:
        return Response({
            "status": "success",
            "message": f"Zmieniono wlasciciela {site_id}: Nowy wlasciciel ID {new_owner_id}",
            "updated_rows": result
        })
    else:
        return Response({
            "status": "error",
            "message": f"Nie udalo sie zmienic wlasciciela {site_id}."
        })


from rest_framework.decorators import api_view
from .models import Cennik


@api_view(['POST'])
def update_parking_price(request, parking_id):
    """
    Update parking price.
    """
    new_price = request.data.get('new_price')

    if not new_price:
        return Response({
            "status": "error",
            "message": "Wymagana nowa cena."
        })

    result = Cennik.objects.filter(parking_id=parking_id).update(cena=new_price)

    if result:
        return Response({
            "status": "success",
            "message": f"Zmieniono rate za strefę ID {parking_id}: Nowa cena {new_price}.",
            "updated_rows": result
        })
    else:
        return Response({
            "status": "error",
            "message": f"Nie udalo sie zmienic ceny dla {parking_id}."
        })


from rest_framework.decorators import api_view
from .models import Rezerwacja


# http://localhost:8000/api/reservations/?status=Wygasla
@api_view(['GET'])
def reservations(request):
    """
    Get reservations filtered by status.
    """
    status = request.GET.get('status')

    if not status:
        return Response({
            "status": "error",
            "message": "Wymagane pole status."
        })

    reservations = Rezerwacja.objects.filter(status=status)

    if reservations.exists():
        data = []
        for reservation in reservations:
            data.append({
                "reservation_id": reservation.id,
                "parking_id": reservation.parking_id,
                "spot_id": reservation.spot_id,
                "start_time": reservation.czas_rozpoczecia,
                "end_time": reservation.czas_zakonczenia,
                "status": reservation.status,
                "price": reservation.cena
            })
        return Response({
            "status": "success",
            "reservations": data
        })
    else:
        return Response({
            "status": "error",
            "message": f"Brak rezerwacji o {status}."
        })


from rest_framework.decorators import api_view


@api_view(['GET'])
def earnings_statistics(request):
    """
    Get total earnings from all payments.
    """
    platnosci = Platnosc.objects.all()
    total_earnings = sum(platnosc.kwota for platnosc in platnosci)

    return Response({
        "status": "success",
        "total_earnings": total_earnings
    })


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Platnosc
from django.db.models import F


@api_view(['GET'])
def user_statistics(request, user_id):
    platnosci = Platnosc.objects.filter(rezerwacja__uzytkownik_id=user_id).values(
        'kwota', 'data_oplaty', 'metoda_platnosci', reservation_id=F('rezerwacja__id')
    )

    if platnosci:
        return Response({
            "status": "success",
            "user_payments": platnosci
        })
    else:
        return Response({
            "status": "error",
            "message": f"Brak platnosci dla uzytkownika {user_id}."
        })


@api_view(['GET'])
def check_spot_availability(request, parking_id):
    """
    Sprawdź, czy w danym parkingu jest dostępne miejsce.
    """
    spot = ParkingSpot.objects.filter(parking_id=parking_id, status="dostepne").first()
    if spot:
        return Response({
            "status": "success",
            "message": "Dostępne miejsce znalezione.",
            "spot_id": spot.id
        })
    else:
        return Response({
            "status": "error",
            "message": "Brak dostępnych miejsc."
        })


from .models import Site, Parking

from .models import SiteSerializer


@api_view(['GET'])
def list_sites(request):
    """
    Zwróć listę wszystkich miejsc oraz ich dostępne parkingi.
    """
    site_id = request.GET.get('id', None)

    if site_id:
        # Filter sites by id
        sites = Site.objects.filter(id=site_id)
    else:
        # Get all sites
        sites = Site.objects.all()

    # Serialize the site data along with the parkings
    serializer = SiteSerializer(sites, many=True)

    return Response(serializer.data)


def home(request):
    return render(request, 'parking_system/home.html')

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
