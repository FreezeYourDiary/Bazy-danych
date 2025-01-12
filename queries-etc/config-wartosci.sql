UPDATE site
SET nazwa = 'Nowa Nazwa', ulica = 'Nowa Ulica', kod_pocztowy = 'Nowy Kod', nr_posesji = 1
WHERE id = 1; -- ID_Site
UPDATE site
SET parking_owner_id = New_ID_P_Owner
WHERE id = 1;-- ID_Site

parking_owner
INSERT INTO rezerwacja (parking_id, spot_id, uzytkownik_id, data_rezerwacji, czas_rozpoczecia, czas_zakonczenia, status, cena)
VALUES (1, 1, 1, CURDATE(), '2025-01-06 08:00:00', '2025-01-06 12:00:00', 'Zarezerwowane', Cena); -- ID_Parking, ID_Parking_spot, ID-Uzytkownik


INSERT INTO `site` (`Parking_Owner_id`, `nazwa`, `ulica`, `kod_pocztowy`, `nr_posesji`)
VALUES
(1, 'Lidl parking', 'ul. Warszawska', '10001', 101),
(2, 'Mitsubishi parking', 'ul.Wrocławska', '10027', 55);


#trzeba poprawic to
INSERT INTO `parking` (`id`, `Site_id`, `nazwa`, `liczba_miejsc`)
VALUES
(1, 1, 'parking dla pracowników' , 20),
(2, 1, 'parking dla użytkowników' , 80),
(3, 1, 'parking dla podziemny' , 16),
(4, 1, 'parking dla samochodów ciężarowych' , 40),
(5, 2, 'parking dla pracowników firmy' , 10),
(6, 2, 'parking dla użytkowników sklepu' , 180);

INSERT INTO rezerwacja (parking_id, spot_id, uzytkownik_id, data_rezerwacji, czas_rozpoczecia, czas_zakonczenia, status, cena)
parking_spotVALUES (1, 1, 1, CURDATE(), '2025-01-06 08:00:00', '2025-01-06 12:00:00', 'Zarezerwowane', Cena);

