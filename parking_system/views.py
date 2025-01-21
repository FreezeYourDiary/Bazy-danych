from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from rest_framework import status
from .services import check_reservation_status, is_spot_available
from django.utils.timezone import now, make_aware
from .models import ParkingSpot, Cennik, Rezerwacja, Platnosc, Site, Parking, Uzytkownik, Pojazd, SpotUsage
from rest_framework.response import Response
from django.db.models import Q, F
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json

import re

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
            filter_conditions &= Q(nazwa__icontains='podziemny')  # do debugu
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

        # pierwsze parking id by bylo response do create reservations
        first_parking_id = parkings.first().id if parkings.exists() else None

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
                "prices": prices,
                "filtered_parking_id": first_parking_id,
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

            if not re.match(r'^\+48\d{9}$', phone):
                return JsonResponse({"error": "Numer telefonu musi zaczynać się od +48 i zawierać 9 cyfr."}, status=400)
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

            request.session['user_id'] = user.id  # store user id w sesji
            return JsonResponse({"message": "Zalogowano pomyślnie."}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def konto_page(request):
    if 'user_id' not in request.session:  # wbudowane sprawdzenie czy logged in
        return redirect(login_page)  # moze tez byc redirect na /home w sumie
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
            return JsonResponse({"logged_in": False, "error": "Nie zalogowany."},
                                status=400)  # user id w sesji nie == wpis w tabeli
    else:
        return JsonResponse({"logged_in": False}, status=200)


''' user functionality '''
@login_required
@require_GET
def list_reservations_api(request):
    user_id = request.session.get('user_id')
    try:
        user = Uzytkownik.objects.get(id=user_id)
        reservations = Rezerwacja.objects.filter(uzytkownik_id=user_id)

        if reservations.exists():
            reservation_list = [
                {
                    "reservation_id": reservation.id,
                    "parking_id": reservation.parking_id,
                    "spot_id": reservation.spot_id,
                    "start_time": reservation.czas_rozpoczecia,
                    "end_time": reservation.czas_zakonczenia,
                    "status": reservation.status,
                    "price": reservation.cena,
                }
                for reservation in reservations
            ]
            return JsonResponse({"reservations": reservation_list}, status=200)
        else:
            return JsonResponse(
                {"message": f"Brak rezerwacji dla uzytkownika {user_id}."},
                status=404
            )
    except Uzytkownik.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
@login_required
def cancel_reservation(request):
    reservation_id = request.data.get('reservation_id')
    if not reservation_id:
        return Response({'error': 'Wymaga ID rezerwacji.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = request.session.get('user_id')
        user = Uzytkownik.objects.get(id=user_id)
        reservation = Rezerwacja.objects.get(id=reservation_id, uzytkownik=user)
    except (Rezerwacja.DoesNotExist, Uzytkownik.DoesNotExist):
        return Response({'error': 'Brak rezerwacji lub nie twoja rezerwacja.'}, status=status.HTTP_400_BAD_REQUEST)
    spot_usage = SpotUsage.objects.filter(spot=reservation.spot, start_data__lt=reservation.czas_zakonczenia,
                                          end_data__gt=reservation.czas_rozpoczecia).first()
    if spot_usage:
        spot_usage.delete()
    reservation.status = 'Anulowana'
    reservation.save()

    return Response({
        'message': 'Anulowano rezerwacje!',
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def pay_for_reservation(request):
    reservation_id = request.data.get('reservation_id')
    payment_amount = request.data.get('payment_amount')

    if not reservation_id:
        return Response({'error': 'Brak ID rezerwacji.'}, status=status.HTTP_400_BAD_REQUEST)
    if not payment_amount:
        return Response({'error': 'Brak kwoty do zapłaty.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        payment_amount = float(payment_amount)
    except ValueError:
        return Response({'error': 'Nieprawidłowa kwota płatności.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = request.session.get('user_id')
        reservation = Rezerwacja.objects.get(id=reservation_id, uzytkownik=user)
    except Rezerwacja.DoesNotExist:
        return Response({'error': 'Rezerwacja nie istnieje lub nie należy do Ciebie.'},
                        status=status.HTTP_404_NOT_FOUND)

    # fix request tu
    if payment_amount != float(reservation.cena):
        return Response({
            'error': f'Kwota płatności ({payment_amount}) nie odpowiada cenie rezerwacji ({reservation.cena}).'
        }, status=status.HTTP_400_BAD_REQUEST)

    payment = Platnosc.objects.create(
        rezerwacja=reservation,
        kwota=payment_amount,
        data_oplaty=datetime.now().date(),
        metoda_platnosci='karta'  # + dodac mozliwosc wyboru metody
    )
    reservation.status = 'Oplacona'
    reservation.save()

    return Response({
        'message': 'Rezerwacja opłacona pomyślnie!',
        'payment_id': payment.id,
        'payment_amount': payment.kwota,
        'payment_date': payment.data_oplaty,
        'payment_method': payment.metoda_platnosci,
    }, status=status.HTTP_200_OK)



@csrf_exempt
@api_view(['POST'])
def create_reservation(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "Nie jestes zalogowany"}, status=401)

        data = request.data
        parking_id = data.get("parking_id")
        vehicle_id = data.get("vehicle_id")
        duration = data.get("duration")

        if not all([vehicle_id, duration]):
            return Response({"error": "Brak parametrow"}, status=400)
        # jesli w request brak first id get it
        first_parking_id = data.get("first_parking_id")
        if first_parking_id:
            parking_id = first_parking_id

        # now time, needs fix with timezones
        start_time = make_aware(datetime.now())
        end_time = start_time + timedelta(hours=int(duration))

        spot = is_spot_available(parking_id)
        if not spot:
            return Response({"error": "Brak dostepnych miejsc"}, status=404)

        try:
            pricing = Cennik.objects.get(parking_id=parking_id)
            total_price = pricing.cena * int(duration)
        except Cennik.DoesNotExist:
            return Response({"error": "Unexpected. Brak ceny dla parkingu"}, status=404)

        reservation = Rezerwacja.objects.create(
            uzytkownik_id=user_id,
            parking_id=parking_id,
            spot_id=spot.id,
            data_rezerwacji=now(),
            czas_rozpoczecia=start_time,
            czas_zakonczenia=end_time,
            status="Zarezerwowana",
            cena=total_price,
        )

        ParkingSpot.objects.filter(id=spot.id).update(status="Zablokowane")

        SpotUsage.objects.create(
            id=vehicle_id,
            parking_id=parking_id,
            spot_id=spot.id,
            start_data=start_time,
            end_data=end_time,
            time_usage=duration,
            cost=total_price,
            rezerwacja=reservation
        )

        Pojazd.objects.create(
            pojazd_id=vehicle_id,
            uzytkownik_id=user_id,
        )

        return Response(
            {
                "message": "Dokonano rezerwacji",
                "reservation_id": reservation.id,
                "total_price": total_price,
            },
            status=201,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@login_required
def get_user_info(request):
    try:
        user_id = request.session.get('user_id')
        user = Uzytkownik.objects.get(id=user_id)
        user_info = {
            'name': user.first_name,
            'lname': user.last_name,
            'phone': user.phone,
            'mail': user.email,
            'type': user.user_type,
            'password': user.password
        }
        return JsonResponse(user_info, status=200)
    except Uzytkownik.DoesNotExist:
        return JsonResponse({'error': 'nie znaleziono uzytkownika'}, status=404)


@csrf_exempt
def update_user_info(request):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            user = Uzytkownik.objects.get(id=user_id)# id from current section
            data = json.loads(request.body)
            name = data.get('name')
            lname = data.get('lname')
            phone = data.get('phone')
            mail = data.get('mail')
            user_type = data.get('type')
            password = data.get('password')

            updated = update_user_info_in_db(user_id, name, lname, phone, mail, user_type, password)

            if updated:
                return JsonResponse({'message': 'zaktualizowano!'}, status=200)
            else:
                return JsonResponse({'error': 'Brak aktualizacji info o uzytkowniku!'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Tylko Metoda POST'}, status=405)


def update_user_info_in_db(user_id, name=None, lname=None, phone=None, mail=None, user_type=None, password=None):
    try:
        # Fetch the user from the database
        user = Uzytkownik.objects.get(id=user_id)

        # Update user fields
        if name:
            user.imie = name
        if lname:
            user.nazwisko = lname
        if phone:
            user.telefon = phone
        if mail:
            user.email = mail
        if password:
            user.password = password

        user.typ = 'default'  # Enforcing 'default'

        user.save()
        print(f"{user_id} zaktualizowano")
        return True
    except Uzytkownik.DoesNotExist:
        print(f" {user_id} nie znaleziono")
        return False
    except Exception as e:
        print(f"Error updating user: {e}")
        return False
