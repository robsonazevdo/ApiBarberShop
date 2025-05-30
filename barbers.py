from flask import Blueprint, request, jsonify
from utils import verify_token
from users import get_user
from datetime import datetime, timedelta
import sqlite3
from consulta import fetch_all_barbers, get_full_barber


barbers = Blueprint('barbers', __name__)
barber = Blueprint('barber', __name__, url_prefix='/barber')

# Lista mockada de barbeiros
# barber_list = [
#     {
#         "id": "1",
#         "name": "Barbeiro 1",
#         "avatar": "https://i.pravatar.cc/150?img=5",
#         "stars": 4.8,
#         "lat": -23.5505,
#         "lng": -46.6333,
#         "loc": "São Paulo",
#         "photos": [
#             "https://i.pravatar.cc/300?img=15",
#             "https://i.pravatar.cc/300?img=16",
#             "https://i.pravatar.cc/300?img=9"
#         ],
#         "services": [
#             { "name": "Corte", "price": 50 },
#             { "name": "Barba", "price": 30 },
#             { "name": "Corte", "price": 50 },
#             { "name": "Barba", "price": 30 }
#         ],
#         "testimonials": [
#             {
#                 "name": "João",
#                 "rate": 5,
#                 "body": "Ótimo corte!"
#             },
#              {
#                 "name": "Rodrigo",
#                 "rate": 4,
#                 "body": "Ótimo corte!"
#             }
#         ],
#         "available": [
#             {
#                 "date": "2025-05-20",
#                 "hours": ["09:00", "10:00", "11:00", "12:00", "15:00", "16:00"]
#             },
#             {
#                 "date": "2025-05-21",
#                 "hours": ["09:00", "10:00", "11:00", "12:00"]
#             },
#             {
#                 "date": "2025-05-22",
#                 "hours": ["09:00", "10:00", "11:00", "12:00"]
#             }
#         ],
#         "appointments": [


#         ]
#     },
#     {
#         "id": "2",
#         "name": "Barbeiro 2",
#         "avatar": "https://i.pravatar.cc/150?img=6",
#         "stars": 4.6,
#         "lat": -23.5595,
#         "lng": -46.6350,
#         "loc": "São Paulo",
#         "favorited": False,
#         "photos": [
#             "https://i.pravatar.cc/300?img=12",
#             "https://i.pravatar.cc/300?img=13",
#             "https://i.pravatar.cc/300?img=14"
#         ],
#         "services": [
#             { "name": "Corte + Barba", "price": 60.0, "duration": "50min" },
#             { "name": "Corte", "price": 40.0, "duration": "30min" },
#             { "name": "Barba", "price": 20.0, "duration": "20min" }
#         ],
#         "testimonials": [
#             { "name": "Lucas", "rate": 5, "body": "Trabalho incrível!" },
#             { "name": "João", "rate": 5, "body": "Trabalho incrível!" }
#         ],
#          "available": [
#             {
#                 "date": "2025-05-20",
#                 "hours": ["09:00", "10:00", "11:00", "12:00", "15:00"]
#             },
#             {
#                 "date": "2025-05-21",
#                 "hours": ["09:00", "10:00", "11:00", "12:00"]
#             },
#             {
#                 "date": "2025-05-22",
#                 "hours": ["09:00", "10:00", "11:00", "12:00", "13:00"]
#             }
#         ],
#         "appointments": [

            
#         ] 
#     },
#     {
#         "id": "3",
#         "name": "Barbeiro 3",
#         "avatar": "https://i.pravatar.cc/150?img=7",
#         "stars": 3.8,
#         "lat": -22.9068,
#         "lng": -43.1729,
#         "loc": "Rio de Janeiro",
#         "favorited": True,
#         "photos": [
#             "https://i.pravatar.cc/300?img=14",
#             "https://i.pravatar.cc/300?img=15",
#             "https://i.pravatar.cc/300?img=17"
#         ],
#         "services": [
#             { "name": "Corte Social", "price": 35.0, "duration": "30min" }
#         ],
#         "testimonials": [
#             { "name": "Pedro", "rate": 4, "body": "Bom atendimento, mas poderia melhorar no tempo." }
#         ],
#          "available": [
#             {
#                 "date": "2025-05-20",
#                 "hours": ["09:00", "10:00", "11:00", "12:00"]
#             },
#             {
#                 "date": "2025-05-21",
#                 "hours": ["09:00", "10:00", "11:00", "12:00"]
#             },
#             {
#                 "date": "2025-05-22",
#                 "hours": ["09:00", "10:00", "11:00", "12:00"]
#             }
#         ],
#         "appointments": [

            
#         ] 
#     }
# ]


@barbers.route('/barbers/all', methods=['GET'])
def get_all_barbers():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token não fornecido"}), 401

    token = auth_header.split(" ")[1]
    decoded = verify_token(token)
    if not decoded:
        return jsonify({ "error": "Token inválido ou expirado", "data": [] }), 401

    user = get_user(decoded.get('email'))
    if not user:
        return jsonify({ "error": "Usuário não encontrado", "data": [] }), 404


    
    return fetch_all_barbers()




@barbers.route('/barbers/search', methods=['GET'])
def search_barbers():
    token = request.args.get('token')
    name_query = request.args.get('name', '').strip().lower()

    if not token:
        return jsonify({ "error": "Token não fornecido", "data": [] }), 401

    decoded = verify_token(token)
    if not decoded:
        return jsonify({ "error": "Token inválido ou expirado", "data": [] }), 401

    user = get_user(decoded.get('email'))
    if not user:
        return jsonify({ "error": "Usuário não encontrado", "data": [] }), 404

    # Consulta ao banco filtrando por nome
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    search_pattern = f"%{name_query}%"
    cur.execute("SELECT * FROM barbers WHERE LOWER(name) LIKE ?", (search_pattern,))
    barbers = cur.fetchall()
    
    data = [dict(row) for row in barbers]

    conn.close()  # ✅ importante

    return jsonify({
        "error": "",
        "data": data
    })





@barbers.route('/barbers', methods=['GET'])
def get_barbers():
    token = request.args.get('token')
    loc = request.args.get('loc')

    if not token:
        return jsonify({ "error": "Token não fornecido", "loc": "", "data": [] }), 401

    decoded = verify_token(token)
    if not decoded:
        return jsonify({ "error": "Token inválido ou expirado", "loc": "", "data": [] }), 401

    user = get_user(decoded.get('email'))
    if not user:
        return jsonify({ "error": "Usuário não encontrado", "loc": "", "data": [] }), 404

    if not loc:
        return jsonify({
            "error": "",
            "loc": "",
            "data": []
        })

    # Consulta ao banco filtrando pela localização
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM barbers WHERE LOWER(loc) = LOWER(?)", (loc,))
    barbers = cur.fetchall()

    data = [dict(barber) for barber in barbers]

    return jsonify({
        "error": "",
        "loc": loc,
        "data": data
    })



@barber.route('/<int:barber_id>', methods=['GET'])
def get_barber(barber_id):
    # Pega o cabeçalho Authorization
    auth_header = request.headers.get('Authorization')

    # Verifica se existe e começa com "Bearer "
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({ "error": "Token não fornecido" }), 401

    # Extrai o token do cabeçalho
    token = auth_header.split(" ")[1]

    # Valida o token
    decoded = verify_token(token)
    if not decoded:
        return jsonify({ "error": "Token inválido ou expirado" }), 401

    # Busca o barbeiro
    barber = get_full_barber(barber_id)

    if not barber:
        return jsonify({ "error": "Barbeiro não encontrado" }), 404

    # Retorna os dados do barbeiro
    return jsonify({
        "error": "",
        "data": barber
    })


def get_barber_by_id(barber_id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM barbers WHERE id = ?", (barber_id,))
    row = cur.fetchone()

    return dict(row) if row else None
