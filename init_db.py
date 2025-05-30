import sqlite3

# Conexão e criação do banco
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Criar tabelas
cursor.executescript('''
DROP TABLE IF EXISTS barbers;
DROP TABLE IF EXISTS photos;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS testimonials;
DROP TABLE IF EXISTS availability;
DROP TABLE IF EXISTS availability_hours;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS favorites;

CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    barber_id INTEGER NOT NULL,
    FOREIGN KEY(user_email) REFERENCES users(email),
    FOREIGN KEY(barber_id) REFERENCES barbers(id),
    UNIQUE(user_email, barber_id) 
);

                     
                     
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    avatar TEXT
);


                     
CREATE TABLE barbers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    avatar TEXT,
    stars REAL,
    lat REAL,
    lng REAL,
    loc TEXT
);

CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barber_id INTEGER,
    url TEXT,
    FOREIGN KEY(barber_id) REFERENCES barbers(id)
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barber_id INTEGER,
    name TEXT,
    price REAL,
    FOREIGN KEY(barber_id) REFERENCES barbers(id)
);

CREATE TABLE testimonials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barber_id INTEGER,
    name TEXT,
    rate INTEGER,
    body TEXT,
    FOREIGN KEY(barber_id) REFERENCES barbers(id)
);

CREATE TABLE availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barber_id INTEGER,
    date TEXT,
    FOREIGN KEY(barber_id) REFERENCES barbers(id)
);

CREATE TABLE availability_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    availability_id INTEGER,
    hour TEXT,
    is_booked BOOLEAN DEFAULT 0,
    FOREIGN KEY(availability_id) REFERENCES availability(id)
);
                     
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    barber_id INTEGER,
    service TEXT,
    datetime TEXT,
    FOREIGN KEY(barber_id) REFERENCES barbers(id)
);
                     

''')

# Dados dos barbeiros
barbers = [
    (1, "Barbeiro 1", "https://i.pravatar.cc/150?img=5", 4.8, -23.5505, -46.6333, "São Paulo"),
    (2, "Barbeiro 2", "https://i.pravatar.cc/150?img=6", 4.6, -23.5595, -46.6350, "São Paulo"),
    (3, "Barbeiro 3", "https://i.pravatar.cc/150?img=7", 3.8, -22.9068, -43.1729, "Rio de Janeiro")
]

cursor.executemany('''
    INSERT INTO barbers (id, name, avatar, stars, lat, lng, loc)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', barbers)

# Fotos
photos = [
    (1, "https://i.pravatar.cc/300?img=15"),
    (1, "https://i.pravatar.cc/300?img=16"),
    (1, "https://i.pravatar.cc/300?img=9"),
    (2, "https://i.pravatar.cc/300?img=12"),
    (2, "https://i.pravatar.cc/300?img=13"),
    (2, "https://i.pravatar.cc/300?img=14"),
    (3, "https://i.pravatar.cc/300?img=14"),
    (3, "https://i.pravatar.cc/300?img=15"),
    (3, "https://i.pravatar.cc/300?img=17")
]

cursor.executemany('INSERT INTO photos (barber_id, url) VALUES (?, ?)', photos)

# Serviços
services = [
    (1, "Corte", 50), (1, "Barba", 30),
    (2, "Corte + Barba", 60), (2, "Corte", 40), (2, "Barba", 20),
    (3, "Corte Social", 35)
]

cursor.executemany('INSERT INTO services (barber_id, name, price) VALUES (?, ?, ?)', services)

# Depoimentos
testimonials = [
    (1, "João", 5, "Ótimo corte!"),
    (1, "Rodrigo", 4, "Ótimo corte!"),
    (2, "Lucas", 5, "Trabalho incrível!"),
    (2, "João", 5, "Trabalho incrível!"),
    (3, "Pedro", 4, "Bom atendimento, mas poderia melhorar no tempo.")
]

cursor.executemany('INSERT INTO testimonials (barber_id, name, rate, body) VALUES (?, ?, ?, ?)', testimonials)

# Inserir availability e availability_hours
availability_raw = [
    (1, "2025-05-27", ["09:00", "10:00", "11:00", "12:00", "15:00", "16:00"]),
    (1, "2025-05-28", ["09:00", "10:00", "11:00", "12:00"]),
    (1, "2025-05-29", ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]),
    (2, "2025-05-28", ["09:00", "10:00", "11:00", "12:00", "15:00"]),
    (2, "2025-05-29", ["09:00", "10:00", "11:00", "12:00"]),
    (2, "2025-05-30", ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]),
    (3, "2025-05-27", ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]),
    (3, "2025-05-28", ["09:00", "10:00", "11:00", "12:00"]),
    (3, "2025-05-29", ["09:00", "10:00", "11:00", "12:00"]),
    (3, "2025-05-30", ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])
]

for barber_id, date, hours in availability_raw:
    cursor.execute('INSERT INTO availability (barber_id, date) VALUES (?, ?)', (barber_id, date))
    availability_id = cursor.lastrowid
    for hour in hours:
        cursor.execute('INSERT INTO availability_hours (availability_id, hour) VALUES (?, ?)', (availability_id, hour))

# Finaliza e fecha
conn.commit()
conn.close()

print("Banco de dados inicializado com sucesso.")
