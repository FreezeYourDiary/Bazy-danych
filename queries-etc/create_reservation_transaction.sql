-- odpowiada nowej rezerwacji
-- Start the transaction
START TRANSACTION;

-- 1. Check if a parking spot is available
SELECT id
FROM parking_spot
WHERE parking_id = 1 AND status = 'dostepne'
LIMIT 1;

-- If no available spot is found, we should roll back the transaction
-- (Check this in your application logic, not directly in SQL)

-- 2. Calculate reservation start and end times
SET @start_time = NOW();
SET @end_time = DATE_ADD(@start_time, INTERVAL 2 HOUR);

-- 3. Get the price per hour
SELECT cena
FROM cennik
WHERE parking_id = 1
LIMIT 1;

-- 4. Calculate total price (e.g., 20.0 price per hour * 2 hours)
SET @total_price = 20.0 * 2;

-- 5. Insert reservation
INSERT INTO rezerwacja (parking_id, spot_id, uzytkownik_id, data_rezerwacji, czas_rozpoczecia, czas_zakonczenia, status, cena)
VALUES (1, 2, 3, CURDATE(), @start_time, @end_time, 'Zarezerwowane', @total_price);

-- 6. Block the parking spot
UPDATE parking_spot
SET status = 'Zablokowane'
WHERE id = 2;

-- 7. Create SpotUsage entry
INSERT INTO spot_usage (parking_id, spot_id, id, start_data, end_data, time_usage, cost, rezerwacja_id)
VALUES (1, 2, @start_time, @end_time, 120, @total_price, LAST_INSERT_ID());

-- 8. Insert vehicle entry
INSERT INTO pojazd (pojazd_id, uzytkownik_id)
VALUES (5, 3);

-- If everything went well, commit the transaction
COMMIT;