-- UNIQUE, NOT NULL, DEFAULT, 

CREATE TABLE Parking_Owner (
	-- ID_P_Owner = id
    -- Nazwa_firmy = nazwa
	id INT AUTO_INCREMENT PRIMARY KEY, -- auto increment , primary key -> unique field
	nazwa VARCHAR(30) not null,
    nazwa_long VARCHAR (255)
);

CREATE TABLE Site (
	id INT auto_increment PRIMARY KEY, -- ID_Site
    Parking_Owner_id INT NOT NULL,
    FOREIGN KEY (Parking_Owner_id) references Parking_Owner(id)
		ON DELETE CASCADE -- wiersze zależne od tablicy są usuwane za pomocą Parking_Owner
        ON UPDATE CASCADE,
    nazwa VARCHAR (255) NOT NULL,
    ulica VARCHAR (255) DEFAULT 'Unknown', -- jesli nie ma zaznaczonej
	kod_pocztowy VARCHAR (8),
    nr_posesji INT
);

CREATE TABLE Parking (
	id INT auto_increment PRIMARY KEY, -- ID_Parking
    Site_id INT NOT NULL,
    FOREIGN KEY (Site_id) references Site(id)
		ON DELETE CASCADE 
        ON UPDATE CASCADE,
    nazwa VARCHAR (255) unique not null,
    liczba_miejsc int not null
);

CREATE TABLE Cennik (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Parking_id INT NOT NULL,     
	FOREIGN KEY (Parking_id) references Parking(id),
    cena float not null
);
CREATE TABLE Atrybuty (
    id INT AUTO_INCREMENT PRIMARY KEY
);
CREATE TABLE Parking_Spot (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- parking spot id
    Parking_id INT NOT NULL,                  -- Foreign key to Parking
    strefa VARCHAR(255) NOT NULL,             -- reference to predefined list
    atrybut INT NOT NULL,                     -- czy int??
    FOREIGN KEY (Parking_id) REFERENCES Parking(id) 
        ON DELETE CASCADE                     
        ON UPDATE CASCADE,
	FOREIGN KEY (atrybut) REFERENCES Atrybuty(id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
-- link do parking spot atrybuty
-- tez dodac link do predefined stref?

CREATE TABLE Spot_Usage (
	Parking_id int not null,
        FOREIGN KEY (Parking_id) REFERENCES Parking(id) 
        ON DELETE CASCADE                     
        ON UPDATE CASCADE,
    Spot_id int not null,
	FOREIGN KEY (Spot_id) REFERENCES Parking_Spot(id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    id varchar(64) PRIMARY KEY, -- numer rejestracyjny pojazdu
    start_data timestamp, -- YYYY-MM-DD HH:MI:SS
    end_data timestamp,
    time_usage int, -- ?? aktualny time usage czy naprzyklad start_data-end_data
    cost float not null
);
CREATE TABLE Rezerwacja (
	id INT AUTO_INCREMENT PRIMARY KEY,   -- id rezerwacji
	Parking_id int not null,
        FOREIGN KEY (Parking_id) REFERENCES Parking(id) 
        ON DELETE CASCADE                     
        ON UPDATE CASCADE,
    Spot_id int not null,
	FOREIGN KEY (Spot_id) REFERENCES Parking_Spot(id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	uzytkownik_id int not null,
	FOREIGN KEY (uzytkownik_id) REFERENCES Uzytkownik(id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
    data_rezerwacji date,
    czas_rozpoczecia datetime,
    czas_zakonczenia datetime,
    status varchar(64) default 'aktywna',
    cena float -- na podstawie czasu wyliczonego 
);
CREATE TABLE Pojazd (
	pojazd_id varchar(64) not null,
	FOREIGN KEY (pojazd_id) REFERENCES Spot_Usage(id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	-- id uzytkownika bierzemy z uzytkownik?
	uzytkownik_id int not null,
	FOREIGN KEY (uzytkownik_id) REFERENCES Uzytkownik(id)
		ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE Uzytkownik (
	id INT auto_increment PRIMARY KEY, -- id uzytkownika
    imie VARCHAR (255) not null,
    nazwisko VARCHAR (255) not null,
    email VARCHAR (255),
    telefon VARCHAR(255) not null,
    typ	char(255) default 'default'
);
CREATE TABLE Platnosc (
	id INT auto_increment PRIMARY KEY, -- id platnosci
	pojazd_id varchar(64) not null,
	FOREIGN KEY (pojazd_id) REFERENCES Spot_Usage(id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	uzytkownik_id int not null,
	FOREIGN KEY (uzytkownik_id) REFERENCES Uzytkownik(id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
        
	kwota float default 0.0, -- moze float -> decimal w przyszlosci
    data_oplaty date,
    metoda_platnosci varchar(16) not null
);

-- testy 
INSERT INTO Parking_Owner (nazwa, nazwa_long) VALUES ('Nazwa', 'Long Nazwa');
describe Parking_Owner;
select * from Parking_Owner;

INSERT INTO Parking_Owner (nazwa, nazwa_long) VALUES ('Druga Nazwa', 'Druga long Nazwa');