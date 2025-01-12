-- opdowiada platnosci
INSERT INTO platnosc (rezerwacja_id, kwota, data_oplaty, metoda_platnosci)
VALUES (1, 20.0, '2025-01-06', 'karta');

	-- + update statusu rezerwacji
UPDATE rezerwacja
SET status = 'oplacono'
WHERE id = 1;

-- rezerwacji by user
SELECT r.id, r.parking_id, r.spot_id, r.czas_rozpoczecia, r.czas_zakonczenia, r.status, r.cena
FROM rezerwacja r
WHERE r.uzytkownik_id = 1;

-- update user, parkingowner etc.
UPDATE uzytkownik
SET imie = 'Admin', nazwisko = '', telefon = '987654321', email = 'admin.parking@gmail.com', typ = 'Admin'
WHERE id = 5;


-- check dostepne miejsca parkingowe
-- SELECT s.id, s.parking_id, s.strefa
-- FROM parking_spot s
-- The LEFT JOIN keyword returns all records from the left table (table1),
-- and the matching records from the right table (table2). The result is 0 records from the right side, if there is no match.
-- LEFT JOIN rezerwacja r ON s.id = r.spot_id AND r.status IN ('Zarezerwowane', 'opłacone') 
--  WHERE r.spot_id IS NULL;

-- zarobki
SELECT SUM(ROUND(p.kwota,2)) AS zarobki
FROM platnosc p;
-- za dzien
SELECT SUM(p.kwota) AS zarobki
from platnosc p
Where DATE(p.data_oplaty) = '2025-01-06'; -- CURDATE();

-- rezerwacji by user
SELECT p.kwota, p.data_oplaty, p.metoda_platnosci, r.id AS reservation_id
FROM platnosc p
-- info z tabeli platnosci dostajemy od rezerwacji, tabela platnosci nie posiada id uzytkownika
JOIN rezerwacja r ON p.rezerwacja_id = r.id
WHERE r.uzytkownik_id = 3;

-- ?user exists
SELECT id, nazwisko
FROM uzytkownik
WHERE telefon = '7336540909';

-- wypisz wszystkie miejsca parkingowe na parkingu
SELECT s.id, s.status AS miejsce
FROM parking_spot s
WHERE s.parking_id = 6;

-- zaimplementowac to do python, 
-- Check if uzytkownik ma rezerwacje, + czy oplacone
SELECT CASE
    -- jesli niema wczesniejszych rezerwacji
    WHEN NOT EXISTS (
        SELECT 1
        FROM rezerwacja r
        WHERE r.uzytkownik_id = 2  -- User ID
    ) THEN 'Użytkownik może zarezerwować, brak wcześniejszych rezerwacji)'
    
    -- jesli zaplacil
    WHEN EXISTS (
        SELECT 1
        FROM platnosc p
        JOIN rezerwacja r ON p.rezerwacja_id = r.id -- id uzytkownika z rezerwacji
        WHERE r.uzytkownik_id = 2  -- User ID
        AND r.status = 'oplacone'  
    ) THEN 'Użytkownik moze zarezerwować'
    
    ELSE 'Uzytkownik nie moze zarezerwować, nie opłacono poprzedniej rezerwacji'
END AS reservation_status;

SELECT nazwa, liczba_miejsc
FROM parking
GROUP BY nazwa, liczba_miejsc
ORDER BY liczba_miejsc ASC;

-- statystyka statusow rezerwacji
select status, count(*)
from rezerwacja
group by status
order by count(*) asc;

-- statystyka oplaconych rezerwacji
select metoda_platnosci, count(*)
from platnosc
group by metoda_platnosci
order by count(*) asc;

-- spot usage jako historia
-- zmiana statusu rezerwacji gdy czas zakonczenia juz minal. na podstawie wspolnego klucza  !join aby potwierdzić istnienie odpowiedniego powiązania między rezerwacją a miejscem parkingowym.
SET SQL_SAFE_UPDATES = 0;
UPDATE rezerwacja r
JOIN parking_spot ps ON r.Parking_id = ps.Parking_id
SET r.status = 'Wygasła'
WHERE r.czas_zakonczenia < NOW() AND r.status = 'Zarezerwowane' or r.status = 'opłacone';
-- na podstawie wynikow zaktualizowanych rezerwacji
-- jesli powiazana rezerwacja wygasla to --->>>
UPDATE parking_spot ps
JOIN rezerwacja r ON ps.Parking_id = r.Parking_id
SET ps.status = 'dostepne'
WHERE r.czas_zakonczenia < NOW() AND r.status = 'Wygasła';

select status, id, Parking_id from parking_spot
where status = 'zablokowane';




