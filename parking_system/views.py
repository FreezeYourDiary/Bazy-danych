from django.shortcuts import render
from .models import ParkingSpot, Cennik, Rezerwacja, Platnosc, Site, Parking, Uzytkownik, Pojazd, SpotUsage

from rest_framework.response import Response

from django.db.models import Q, F
from rest_framework.decorators import api_view

from django.views.decorators.csrf import csrf_exempt
import json
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

def signup_page(request):
    return render(request, 'parking_system/signup.html')

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone = data.get('phone', 'unknown')
            password = data.get('password')

            # Check if email already exists
            if Uzytkownik.objects.filter(email=email).exists():
                return JsonResponse({"error": "Uzytkownik o podanym email istnieję."}, status=400)

            # Create user
            user = Uzytkownik(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password
            )
            user.save()
            return JsonResponse({"message": "Dziękujemy za rejestracje w systemie."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def login_page(request):
    return render(request, 'parking_system/login.html')

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = Uzytkownik.objects.filter(email=email).first()
            if user is None:
                return JsonResponse({"error": "Nie znaleziono użytkownika o podanym email."}, status=400)

            if user.password != password:
                return JsonResponse({"error": "Niepoprawne hasło."}, status=400)

            request.session['user_id'] = user.id # store user id w sesji
            return JsonResponse({"message": "Zalogowano pomyślnie."}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def konto_page(request):
    if 'user_id' not in request.session:  # wbudowane sprawdzenie czy logged in
        return redirect(login_page) # moze tez byc redirect na /home w sumie
    # render the Konto page/
    user_id = request.session.get('user_id')
    user = Uzytkownik.objects.get(id=user_id)
    return render(request, 'parking_system/konto.html', {
        'user': user,
    })
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect(login_page)
def is_logged_in(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Uzytkownik.objects.get(pk=user_id)
            return JsonResponse({
                "logged_in": True,
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }, status=200)
        except Uzytkownik.DoesNotExist:
            return JsonResponse({"logged_in": False, "error": "Invalid user session."}, status=400) # user id w sesji nie == wpis w tabeli
    else:
        return JsonResponse({"logged_in": False}, status=200)

from django.http import JsonResponse
from django.shortcuts import redirect
''' reservations '''


