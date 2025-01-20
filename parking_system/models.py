# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * !!!!  Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.hashers import make_password
from django.db import models


class Atrybuty(models.Model):

    class Meta:
        managed = False
        db_table = 'atrybuty'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Cennik(models.Model):
    parking = models.ForeignKey('Parking', models.DO_NOTHING, db_column='Parking_id')
    cena = models.FloatField()

    class Meta:
        managed = False
        db_table = 'cennik'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Parking(models.Model):
    site = models.ForeignKey('Site', models.DO_NOTHING, db_column='Site_id')  # Field name made lowercase.
    nazwa = models.CharField(unique=True, max_length=255)
    liczba_miejsc = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'parking'


class ParkingOwner(models.Model):
    nazwa = models.CharField(max_length=30)
    nazwa_long = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parking_owner'


class ParkingSpot(models.Model):
    parking = models.ForeignKey(Parking, models.DO_NOTHING, db_column='Parking_id', default='1')  # Field name made lowercase.
    strefa = models.CharField(max_length=255)
    atrybut = models.ForeignKey(Atrybuty, models.DO_NOTHING, db_column='atrybut', default='1')
    status = models.CharField(max_length=20, default="dostępne")  # Available, Blocked
    class Meta:
        managed = True
        db_table = 'parking_spot'


class Platnosc(models.Model):
    # pojazd = models.ForeignKey('SpotUsage', models.DO_NOTHING)
    # uzytkownik = models.ForeignKey('Uzytkownik', models.DO_NOTHING)

    # foreign key to rezerwacja not pojazd/uzytkownik
    rezerwacja = models.ForeignKey('Rezerwacja', models.DO_NOTHING)

    kwota = models.FloatField(blank=True, null=True)
    data_oplaty = models.DateField(blank=True, null=True)
    metoda_platnosci = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'platnosc'


class Pojazd(models.Model):
    pojazd_id = models.CharField(max_length=64)
    uzytkownik = models.ForeignKey('Uzytkownik', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pojazd'


class Rezerwacja(models.Model):
    parking = models.ForeignKey(Parking, models.DO_NOTHING, db_column='Parking_id')
    spot = models.ForeignKey(ParkingSpot, models.DO_NOTHING, db_column='Spot_id')
    uzytkownik = models.ForeignKey('Uzytkownik', models.DO_NOTHING)
    data_rezerwacji = models.DateField(blank=True, null=True)
    czas_rozpoczecia = models.DateTimeField(blank=True, null=True)
    czas_zakonczenia = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)
    cena = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rezerwacja'


class Site(models.Model):
    parking_owner = models.ForeignKey(ParkingOwner, models.DO_NOTHING, db_column='Parking_Owner_id')
    nazwa = models.CharField(max_length=255)
    ulica = models.CharField(max_length=255, blank=True, null=True)
    kod_pocztowy = models.CharField(max_length=8, blank=True, null=True)
    nr_posesji = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'site'


class SpotUsage(models.Model):
    parking = models.ForeignKey(Parking, models.DO_NOTHING, db_column='Parking_id')
    spot = models.ForeignKey(ParkingSpot, models.DO_NOTHING, db_column='Spot_id')
    rezerwacja = models.ForeignKey(Rezerwacja, models.DO_NOTHING, db_column='Rezerwacja_id', null=True, blank=True)
    id = models.CharField(primary_key=True, max_length=64)
    start_data = models.DateTimeField(blank=True, null=True)
    end_data = models.DateTimeField(blank=True, null=True)
    time_usage = models.IntegerField(blank=True, null=True)
    cost = models.FloatField()

    class Meta:
        managed = False
        db_table = 'spot_usage'



class Uzytkownik(models.Model):
    first_name = models.CharField(max_length=255, db_column='imie')
    last_name = models.CharField(max_length=255, db_column='nazwisko')
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=255, default='unknown', db_column='telefon')
    user_type = models.CharField(max_length=255, default='default', db_column='typ')
    password = models.CharField(max_length=500)

    # def save(self, *args, **kwargs):
    #     if not self.pk or not self.password.startswith('pbkdf2_'):  # Only hash if new or unhashed
    #         self.password = make_password(self.password)
    #     super(Uzytkownik, self).save(*args, **kwargs)

    class Meta:
        db_table = 'uzytkownik'


from rest_framework import serializers
from .models import Site, Parking

class SiteSerializer(serializers.ModelSerializer):
    parkings = serializers.SerializerMethodField()  # Custom field for parking names

    class Meta:
        model = Site
        fields = ['id', 'nazwa', 'ulica', 'kod_pocztowy', 'nr_posesji', 'parkings']

    def get_parkings(self, obj):
        # Get all parkings for this site and return only the 'nazwa' field
        parkings = Parking.objects.filter(site=obj)
        return [parking.nazwa for parking in parkings]

