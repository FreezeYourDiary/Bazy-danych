from django.shortcuts import render
from .models import ParkingSpot, Cennik, Rezerwacja, Platnosc, Site, Parking, Uzytkownik
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, F
from rest_framework.decorators import api_view

''' HOME PAGE REQUESTS'''
# views.py
@api_view(['GET'])
def available_parking_spots_with_filters(request, site_id):
    try:
    # lista filtrow
        filters = request.GET.getlist('filters')
        print(f"Received filters: {filters}")

        site = Site.objects.get(id=site_id)
        parkings = Parking.objects.filter(site=site)

        filter_conditions = Q()
        if 'podziemny' in filters:
            filter_conditions &= Q(nazwa__icontains='podziemny') # do debugu
            print("Filter condition for podziemny added")
        if 'pracownikow' in filters:
            filter_conditions &= Q(nazwa__icontains='pracownikow')
            print("Filter condition for pracownikow added")
        if 'ciezarowych' in filters:
            filter_conditions &= Q(nazwa__icontains='ciezarowych')
            print("Filter condition for ciezarowych added")

        print(f"Filter conditions: {filter_conditions}")

        parkings = parkings.filter(filter_conditions)

        print(f"Filtered parking spots: {parkings}")

        available_spots = ParkingSpot.objects.filter(parking__in=parkings, status="dostępne").count()
        prices = {}
        for parking in parkings:
            try:
                cennik = Cennik.objects.get(parking=parking)
                prices[parking.id] = cennik.cena
            except Cennik.DoesNotExist:
                prices[parking.id] = "Cena niedostępna"
        if available_spots > 0:
            return Response({
                "site_id": site_id,
                "available_spots": available_spots,
                "prices": prices  # Add the price information
            })
        else:
            return Response({"message": "Brak dostępnych miejsc dla wybranych filtrów."}, status=404)
    except Site.DoesNotExist:
        return Response({"message": "Nie znaleziono podanego parku."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def search_parking(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return Response({"error": "Brak zapytania."}, status=400)
    try:
        site = Site.objects.filter(
            Q(nazwa__icontains=query) |
            Q(ulica__icontains=query) |
            Q(kod_pocztowy__icontains=query)
        ).first()

        if site:
            parking = Parking.objects.filter(site=site).first()
            if parking:
                return Response({"parking_id": parking.id})
        return Response({"error": "Nie znaleziono parkingu."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def autocomplete_sites(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return Response({"results": []})  # puste zapytanie??

    try:
        # filtracja podobienstwa
        sites = Site.objects.filter(
            Q(nazwa__icontains=query) |
            Q(ulica__icontains=query) |
            Q(kod_pocztowy__icontains=query)
        ).values('id', 'nazwa', 'ulica', 'kod_pocztowy')[:10]

        return Response({"results": list(sites)})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


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

def home(request):
    return render(request, 'parking_system/home.html')
def login_signup(request):
    return render(request, 'parking_system/login-signup.html')


