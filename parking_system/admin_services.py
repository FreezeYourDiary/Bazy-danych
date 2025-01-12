from .models import Site


def update_parking_details(site_id, nazwa=None, ulica=None, kod_pocztowy=None, nr_posesji=None):
    result = Site.objects.filter(id=site_id).update(
        nazwa=nazwa,
        ulica=ulica,
        kod_pocztowy=kod_pocztowy,
        nr_posesji=nr_posesji
    )
    print(f"Zmieniono info o Site ID {site_id}: {result} row(s) affected.")


# Update parking owner
def update_parking_owner(site_id, new_owner_id):
    result = Site.objects.filter(id=site_id).update(parking_owner_id=new_owner_id)
    print(f"Zmieniono wlasciciela {site_id}: Nowy wlasciciel ID {new_owner_id}, {result} row(s) affected.")


from .models import Cennik, Rezerwacja


def update_parking_price(parking_id, new_price):
    result = Cennik.objects.filter(parking_id=parking_id).update(cena=new_price)
    print(f"Zmieniono rate za strefę ID {parking_id}: Nowa cena {new_price}, {result} row(s) affected.")


# statystyka
def reservations(status):
    reservations = Rezerwacja.objects.filter(status=status)
    if reservations.exists():
        for reservation in reservations:
            print(f"Reservation ID: {reservation.id}")
            print(f"Parking ID: {reservation.parking_id}")
            print(f"Spot ID: {reservation.spot_id}")
            print(f"Start Time: {reservation.czas_rozpoczecia}")
            print(f"End Time: {reservation.czas_zakonczenia}")
            print(f"Status: {reservation.status}")
            print(f"Price: {reservation.cena}")
            print("-" * 40)
    else:
        print(f"Brak rezerwacji o stanie {status}.")


from .models import Platnosc


def stat_zysk(data=None):
    platnosci = Platnosc.objects.all()
    total_earnings = sum(platnosc.kwota for platnosc in platnosci)
    print(total_earnings)


from django.db.models import F


def stat_user(user_id):
    platnosci = Platnosc.objects.filter(rezerwacja__uzytkownik_id=user_id).values(
        'kwota', 'data_oplaty', 'metoda_platnosci', reservation_id=F('rezerwacja__id')
    )
    return platnosci
