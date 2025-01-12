from .models import ParkingSpot, Rezerwacja, SpotUsage, Platnosc, Cennik, Pojazd, Uzytkownik

def show_parking_price(parking_id):
    price = Cennik.objects.filter(parking_id=parking_id).values_list('cena', flat=True)
    print(f"Cena za strefę {parking_id}: {list(price)}/godz.")

# first available spot to book -- used in reservation
def is_spot_available(parking_id):
    from .models import ParkingSpot
    spot = ParkingSpot.objects.filter(parking_id=parking_id, status="dostepne").first()
    return spot if spot else None

def calculate_price(parking_id, hours):
    from .models import Cennik
    price_per_hour = Cennik.objects.filter(parking_id=parking_id).values_list('cena', flat=True).first()
    return price_per_hour * hours

from datetime import datetime, timedelta


def add_user(name, lname, email=None, phone=None, type=None):
    if email and Uzytkownik.objects.filter(email=email).exists():
        raise ValueError("Email jest już zarejestrowany.")

    user_type = "default" if type is None else type

    user = Uzytkownik.objects.create(
        imie=name,
        nazwisko=lname,
        telefon=phone,
        email=email,
        typ=user_type
    )
    return user

def create_reservation(parking_id, hours, user_id, vehicle_id):
    # 1 spot musi byc dostepny na parkingu
    spot = is_spot_available(parking_id)
    if not spot:
        raise ValueError("Brak dostępnych miejsc.")
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=hours)

    total_price = calculate_price(parking_id, hours)
    # wpis do rezerwacji -- czas startu in zakonczenia na podstawie godzin
    reservation = Rezerwacja.objects.create(
        parking_id=parking_id,
        spot_id=spot.id,
        uzytkownik_id=user_id,
        data_rezerwacji=start_time.date(),
        czas_rozpoczecia=start_time,
        czas_zakonczenia=end_time,
        status='Zarezerwowane',
        cena=total_price
    )
    # block parking spot
    ParkingSpot.objects.filter(id=spot.id).update(status='Zablokowane')

    # spotusage tu jako historia wpisow-miejsc parkingowych
    # jedno miejsce dostaje wpisy od wielu rezerwacji nie wzajemnych
    SpotUsage.objects.create(
        id=vehicle_id,
        parking_id=parking_id,
        spot_id=spot.id,
        start_data=start_time,
        end_data=end_time,
        time_usage=hours * 60,
        cost=total_price,
        rezerwacja=reservation
    )

    # link samochodu do uzytkownika
    Pojazd.objects.create(
        pojazd_id=vehicle_id,
        uzytkownik_id=user_id
    )


    print(f"Dokonano rezerwacji: {reservation}")
    return reservation


def create_payment_for_reservation(reservation_id, payment_amount, payment_method):
    try:
        reservation = Rezerwacja.objects.get(id=reservation_id)
        # wpis do platnosci/ !nie ma logiki kwot
        Platnosc.objects.create(
            rezerwacja=reservation,  # Link the payment to the reservation
            kwota=payment_amount,
            data_oplaty=datetime.now(),  # Current date/time for payment
            metoda_platnosci=payment_method
        )

        reservation.status = "oplacone"
        reservation.save()

        print(f"Zarejestrowano platnosc dla rezerwacji {reservation_id}.")

    except Rezerwacja.DoesNotExist:
        print(f"Nie istnieje rezerwacji {reservation_id}.")


def cancel_reservation(reservation_id):
    try:
        reservation = Rezerwacja.objects.get(id=reservation_id)
        if reservation.status == "anulowane":
            print(f"Rezerwację {reservation_id} juz anulowano.")
            return

        reservation.status = "anulowane"
        reservation.save()
        spot_usage = SpotUsage.objects.filter(spot=reservation.spot, start_data__lt=reservation.czas_zakonczenia,
                                              end_data__gt=reservation.czas_rozpoczecia).first()
        if spot_usage:
            spot_usage.delete()  # przykladowo jesli anulowalismy rez. to nie trzeba wpisu

        print(f"Rezerwację {reservation_id} anulowano.")

    except Rezerwacja.DoesNotExist:
        print(f"Nie istnieje rezerwacji {reservation_id}.")

def check_reservation_status(user_id):
    previous_res = Rezerwacja.objects.filter(uzytkownik_id=user_id).exists()
    paid_previous_res = Platnosc.objects.filter(
        rezerwacja__uzytkownik_id=user_id,
        rezerwacja__status='oplacone'
    ).exists()

    if not previous_res:
        return 'Użytkownik może zarezerwować, brak wcześniejszych rezerwacji'
    elif paid_previous_res:
        return 'Użytkownik może zarezerwować'
    else:
        return 'Użytkownik nie może zarezerwować, nie opłacono poprzedniej rezerwacji'

# Example usage
def update_user_info(user_id, name=None, lname=None, phone=None, mail=None, type=None):
    try:
        user = Uzytkownik.objects.get(id=user_id)

        if name:
            user.imie = name
        if lname:
            user.nazwisko = lname
        if phone:
            user.telefon = phone
        if mail:
            user.email = mail
        if type:
            user.typ = type
        user.save()
        print(f"User {user_id} info zaltualizowano.")

    except Uzytkownik.DoesNotExist:
        print(f"W bazie nie istnieje uzytkownika {user_id} - not found.")
    except Exception as e:
        print(f"default error: {e}")

def list_reservations_by_user(user_id):
    try:
        reservations = Rezerwacja.objects.filter(uzytkownik_id=user_id)
        if reservations.exists():
            print(f"Reservations for User ID {user_id}:")
            for reservation in reservations:
                # opcjonalnie dodac jako parametr do funkcji wyswietlenie tylko jednego z parametrow
                print(f"Reservation ID: {reservation.id}")
                print(f"Parking ID: {reservation.parking_id}")
                print(f"Spot ID: {reservation.spot_id}")
                print(f"Start Time: {reservation.czas_rozpoczecia}")
                print(f"End Time: {reservation.czas_zakonczenia}")
                print(f"Status: {reservation.status}")
                print(f"Price: {reservation.cena}")
                print("-" * 40)
        else:
            print(f"Zadnej rezerwacji dla uzytkownika {user_id}.")
    except Exception as e:
        print(f"Default error: {e}")