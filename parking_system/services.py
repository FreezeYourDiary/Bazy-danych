from .models import Site


# update info about parking
def update_parking_details(site_id, nazwa, ulica, kod_pocztowy, nr_posesji):
    result = Site.objects.filter(id=site_id).update(
        nazwa=nazwa,
        ulica=ulica,
        kod_pocztowy=kod_pocztowy,
        nr_posesji=nr_posesji
    )
    print(f"Updated parking details for Site ID {site_id}: {result} row(s) affected.")


# Update parking owner
def update_parking_owner(site_id, new_owner_id):
    result = Site.objects.filter(id=site_id).update(parking_owner_id=new_owner_id)
    print(f"Updated owner for Site ID {site_id}: New Owner ID {new_owner_id}, {result} row(s) affected.")

from .models import Rezerwacja, ParkingSpot, SpotUsage

def create_reservation(parking_id, spot_id, user_id, start_time, end_time, cena):
    rezerwacja = Rezerwacja.objects.create(
        parking_id=parking_id,
        spot_id=spot_id,
        uzytkownik_id=user_id,
        data_rezerwacji=start_time.date(),
        czas_rozpoczecia=start_time,
        czas_zakonczenia=end_time,
        status='Zarezerwowane',
        cena=cena
    )
    ParkingSpot.objects.filter(id=spot_id).update(status='Zablokowane')

    SpotUsage.objects.create(
        parking_id=parking_id,
        spot_id=spot_id,
        start_data=start_time,
        end_data=end_time,
        time_usage=(end_time - start_time).seconds // 60,
        cost=cena
    )
    return rezerwacja


def cancel_reservation(reservation_id):
    from .models import Rezerwacja, ParkingSpot

    try:
        reservation = Rezerwacja.objects.get(id=reservation_id)
        ParkingSpot.objects.filter(id=reservation.spot_id).update(status='Dostępne')
        reservation.delete()
    except Rezerwacja.DoesNotExist:
        return False
    return True


from .models import Platnosc
import datetime
def record_payment(pojazd_id, user_id, kwota, metoda_platnosci):
    Platnosc.objects.create(
        pojazd_id=pojazd_id,
        uzytkownik_id=user_id,
        kwota=kwota,
        data_oplaty=datetime.date.today(),
        metoda_platnosci=metoda_platnosci
    )


from .models import Cennik
def update_parking_price(parking_id, new_price):
    Cennik.objects.filter(parking_id=parking_id).update(cena=new_price)

def show_parking_price(parking_id):
    print(Cennik.objects.filter(parking_id=parking_id))