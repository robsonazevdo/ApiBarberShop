import sqlite3
from flask import jsonify
from datetime import datetime as dt




def add_user(email, name, hashed_password):
    try:
        avatar = f'https://i.pravatar.cc/150?u={email}'
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (email, name, password, avatar)
            VALUES (?, ?, ?, ?)
        ''', (email, name, hashed_password, avatar))

        conn.commit()
        conn.close()
        return True, "Usuário cadastrado com sucesso"
    except sqlite3.IntegrityError:
        return False, "Usuário já existe"
    except Exception as e:
        return False, str(e)

    
def get_user_by_email(email):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None

    

def fetch_all_barbers():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Busca todos os barbeiros
    cursor.execute("SELECT * FROM barbers")
    barber_rows = cursor.fetchall()

    barbers = []

    for barber in barber_rows:
        barber_id = barber["id"]

        # Fotos
        cursor.execute("SELECT url FROM photos WHERE barber_id = ?", (barber_id,))
        photos = [row["url"] for row in cursor.fetchall()]

        # Serviços
        cursor.execute("SELECT name, price FROM services WHERE barber_id = ?", (barber_id,))
        services = [dict(row) for row in cursor.fetchall()]

        # Testemunhos
        cursor.execute("SELECT name, rate, body FROM testimonials WHERE barber_id = ?", (barber_id,))
        testimonials = [dict(row) for row in cursor.fetchall()]

        # Disponibilidade (dias e horas)
        cursor.execute("SELECT id, date FROM availability WHERE barber_id = ?", (barber_id,))
        availability = []
        for avail in cursor.fetchall():
            avail_id = avail["id"]
            cursor.execute("SELECT hour FROM availability_hours WHERE id = ?", (avail_id,))
            hours = [h["hour"] for h in cursor.fetchall()]
            availability.append({
                "date": avail["date"],
                "hours": hours
            })

        # Monta o dicionário final
        barbers.append({
            "id": str(barber["id"]),
            "name": barber["name"],
            "avatar": barber["avatar"],
            "stars": barber["stars"],
            "lat": barber["lat"],
            "lng": barber["lng"],
            "loc": barber["loc"],
            "photos": photos,
            "services": services,
            "testimonials": testimonials,
            "available": availability,
            "appointments": []  # futuramente pode ser preenchido
        })

    conn.close()
    return jsonify({"error": "", "data": barbers})



def get_full_barber(barber_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Dados principais
    cur.execute("SELECT * FROM barbers WHERE id = ?", (barber_id,))
    barber = cur.fetchone()
    if not barber:
        return None

    barber_data = dict(barber)

    # Fotos
    cur.execute("SELECT url FROM photos WHERE barber_id = ?", (barber_id,))
    barber_data["photos"] = [row["url"] for row in cur.fetchall()]

    # Serviços
    cur.execute("SELECT name, price FROM services WHERE barber_id = ?", (barber_id,))
    barber_data["services"] = [dict(row) for row in cur.fetchall()]

    # Depoimentos
    cur.execute("SELECT name, rate, body FROM testimonials WHERE barber_id = ?", (barber_id,))
    barber_data["testimonials"] = [dict(row) for row in cur.fetchall()]

    # Disponibilidade (somente horários disponíveis: is_booked = 0)
    cur.execute("SELECT id, date FROM availability WHERE barber_id = ?", (barber_id,))
    availability_rows = cur.fetchall()
    available = []

    for row in availability_rows:
        availability_id = row["id"]
        cur.execute("""
            SELECT hour FROM availability_hours 
            WHERE availability_id = ? AND is_booked = 0
        """, (availability_id,))
        
        hours = [h["hour"] for h in cur.fetchall()]
        
        # Só adiciona a data se houver horários disponíveis
        if hours:
            available.append({
                "date": row["date"],
                "hours": hours
            })

    barber_data["available"] = available

    return barber_data




def create_appointments(user_email, barber_id, service, datetime_str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Inserir o agendamento
    cursor.execute('''
        INSERT INTO appointments (user_email, barber_id, service, datetime)
        VALUES (?, ?, ?, ?)
    ''', (user_email, barber_id, service, datetime_str))

    appointment_id = cursor.lastrowid

    # Extrair data e hora no formato certo
    date_part, time_part = datetime_str.split(" ")

    # Corrigir formato de hora para HH:MM
    time_part = dt.strptime(time_part, "%H:%M:%S").strftime("%H:%M")

    print(barber_id, date_part, time_part)

    cursor.execute('''
        UPDATE availability_hours
        SET is_booked = 1
        WHERE hour = ? AND availability_id IN (
            SELECT id FROM availability
            WHERE barber_id = ? AND date = ?
        )
    ''', (time_part, barber_id, date_part))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "appointment": {
            "id": appointment_id,
            "user_email": user_email,
            "barber_id": barber_id,
            "service": service,
            "datetime": datetime_str
        }
    }), 201



def get_appointments_by_user(email):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.id, a.barber_id, a.service, a.datetime, b.name, b.avatar, s.price
        FROM appointments a
        JOIN barbers b ON a.barber_id = b.id
        LEFT JOIN services s ON s.barber_id = b.id AND s.name = a.service
        WHERE a.user_email = ?
        ORDER BY a.datetime DESC
    ''', (email,))
    
    results = cursor.fetchall()
    conn.close()

    appointments = []
    for row in results:
        appointment = {
            "id": row[0],
            "barber_id": row[1],
            "service": row[2],
            "datetime": row[3],
            "barber_name": row[4],
            "barber_avatar": row[5],
            "price": row[6] if row[6] is not None else 0.0
        }
        appointments.append(appointment)

    return appointments



def get_appointment_by_id(appointment_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.id, a.user_email, a.barber_id, a.service, a.datetime
        FROM appointments a
        WHERE a.id = ?
    ''', (appointment_id,))
    
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "id": result[0],
            "user_email": result[1],
            "barber_id": result[2],
            "service": result[3],
            "datetime": result[4]
        }
    return None


def delete_appointment_by_id(appointment_id):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Buscar datetime original
        cursor.execute('SELECT barber_id, datetime FROM appointments WHERE id = ?', (appointment_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False, "Agendamento não encontrado"

        barber_id, datetime_value = result
        date_part, time_part = datetime_value.split(" ")

        # ✅ Corrigir o formato da hora (remover segundos)
        time_part = dt.strptime(time_part, "%H:%M:%S").strftime("%H:%M")

        # Deletar o agendamento
        cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))

        # Liberar horário (set is_booked = 0)
        cursor.execute('''
            UPDATE availability_hours
            SET is_booked = 0
            WHERE hour = ? AND availability_id IN (
                SELECT id FROM availability
                WHERE barber_id = ? AND date = ?
            )
        ''', (time_part, barber_id, date_part))

        conn.commit()
        conn.close()
        return True, "Agendamento removido com sucesso"

    except Exception as e:
        return False, str(e)



def toggle_favorite(user_email, barber_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Verifica se já existe
    cursor.execute('SELECT id FROM favorites WHERE user_email=? AND barber_id=?', (user_email, barber_id))
    result = cursor.fetchone()

    if result:
        # Já está favoritado: remove
        cursor.execute('DELETE FROM favorites WHERE id=?', (result[0],))
        conn.commit()
        conn.close()
        return False  # desfavoritado
    else:
        # Adiciona como favorito
        cursor.execute('INSERT INTO favorites (user_email, barber_id) VALUES (?, ?)', (user_email, barber_id))
        conn.commit()
        conn.close()
        return True  # favoritado
    


def get_favorites(user_email):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT b.id, b.name, b.avatar, b.stars, b.lat, b.lng, b.loc
            FROM favorites f
            JOIN barbers b ON f.barber_id = b.id
            WHERE f.user_email = ?
        ''', (user_email,))
        results = cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "avatar": row[2],
                "stars": row[3],
                "lat": row[4],
                "lng": row[5],
                "loc": row[6]
            }
            for row in results
        ]
    finally:
        conn.close()



def is_favorited(user_email, barber_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM favorites WHERE user_email=? AND barber_id=?', (user_email, barber_id))
    result = cursor.fetchone()
    conn.close()
    return True if result else False
