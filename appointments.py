from flask import Blueprint, request, jsonify
from utils import verify_token
from users import get_user
from consulta import create_appointments, delete_appointment_by_id, get_appointments_by_user, get_appointment_by_id

appointments = Blueprint('appointments', __name__)


@appointments.route('/appointments', methods=['POST'])
def create_appointment():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token não fornecido"}), 401

    token = auth_header.split(" ")[1]
    decoded = verify_token(token)

    if not decoded:
        return jsonify({"error": "Token inválido"}), 401

    user = get_user(decoded["email"])
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    data = request.get_json()
    barber_id = data.get("barber_id")
    service = data.get("service")
    datetime_value = data.get("datetime")

    if not all([barber_id, service, datetime_value]):
        return jsonify({"error": "Dados incompletos"}), 400


    return create_appointments(user["email"], barber_id, service, datetime_value)
    


@appointments.route('/appointments', methods=['GET'])
def list_appointments():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token não fornecido"}), 401

    token = auth_header.split(" ")[1]
    decoded = verify_token(token)

    if not decoded:
        return jsonify({"error": "Token inválido"}), 401

    user = get_user(decoded["email"])
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    try:
        appointments = get_appointments_by_user(user["email"])
        return jsonify({"appointments": appointments})
    except Exception as e:
        return jsonify({"error": "Erro ao buscar agendamentos", "details": str(e)}), 500
    

    

@appointments.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token não fornecido"}), 401

    token = auth_header.split(" ")[1]
    decoded = verify_token(token)

    if not decoded:
        return jsonify({"error": "Token inválido"}), 401

    user = get_user(decoded["email"])
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        return jsonify({"error": "Agendamento não encontrado"}), 404

    if appointment["user_email"] != user["email"]:
        return jsonify({"error": "Permissão negada"}), 403

    success, message = delete_appointment_by_id(appointment_id)
    if not success:
        return jsonify({"error": "Erro ao deletar agendamento", "details": message}), 500

    return jsonify({"success": True, "message": message}), 200