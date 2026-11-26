#index.py
import os
import math
from datetime import datetime
from flask import Flask, jsonify, request
import db

app = Flask(__name__)
app.debug = os.getenv('FLASK_DEBUG') == '1'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')   # definir na Vercel (sem valor por omissão)

OK_CODE = 200
SUCCESS_CODE = 201
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
CONFLICT_CODE = 409
SERVER_ERROR = 500

COMANDOS_VALIDOS = ["fan_on", "fan_off", "alarm_on", "alarm_off"]

def device_existe(id_device):
    try:
        return db.obter_device_id(id_device) is not None
    except Exception:
        return None

#NIF português: 9 dígitos
def nif_valido(nif):
    return len(nif) == 9 and nif.isdigit()

#Validação simples de email
def email_valido(email):
    return "@" in email and "." in email.split("@")[-1]


@app.errorhandler(404)
def rota_nao_encontrada(e):
    return jsonify({"error": "Rota não encontrada"}), NOT_FOUND

@app.errorhandler(405)
def metodo_nao_permitido(e):
    return jsonify({"error": "Método não permitido"}), METHOD_NOT_ALLOWED

@app.errorhandler(500)
def erro_servidor(e):
    return jsonify({"error": "Erro interno do servidor"}), SERVER_ERROR


#PAGINA ENTRADA
@app.route('/', methods=["GET"])
def home():
    return "Bem-Vindo à Sala de Servidores da ESTGOH"


# ======================= AUTH / USERS =======================

#REGISTER
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    # aceita "name" ou "nome"
    nome = data.get("name")
    email = data.get("email")
    password = data.get("password")
    nif = str(data.get("nif") or "").strip()

    if not nome or not email or not password or not nif:
        return jsonify({"error": "Faltam campos obrigatórios"}), BAD_REQUEST_CODE

    if not email_valido(email):
        return jsonify({"error": "Email inválido"}), BAD_REQUEST_CODE

    if not nif_valido(nif):
        return jsonify({"error": "NIF inválido (9 dígitos)"}), BAD_REQUEST_CODE

    resultado = db.add_user(nome, email, password, nif)

    if resultado == 'SUCESSO':
        return jsonify({"message": "Utilizador adicionado com sucesso"}), SUCCESS_CODE

    if resultado == 'EMAIL_EXISTE':
        return jsonify({"error": "Email já registado"}), CONFLICT_CODE

    if resultado == 'NIF_EXISTE':
        return jsonify({"error": "NIF já registado"}), CONFLICT_CODE

    return jsonify({"error": "Erro interno ao registar utilizador"}), SERVER_ERROR


#LOGIN
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Falta de dados obrigatórios"}), BAD_REQUEST_CODE

    resultado = db.adiciona_logs(data["email"], data["password"])

    if resultado is None:
        return jsonify({"error": "Erro interno ao iniciar sessão"}), SERVER_ERROR

    if not resultado["sucesso"]:
        return jsonify({"error": resultado["mensagem"]}), UNAUTHORIZED_CODE

    return jsonify(resultado), OK_CODE


#listar users
@app.route('/api/users', methods=['GET'])
def listar_users():
    resultado = db.lista_users()

    if resultado is None:
        return jsonify({"error": "Erro ao listar utilizadores"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE


#obter user por id
@app.route('/api/users/<int:id>', methods=['GET'])
def listar_user_id(id):
    resultado = db.obter_user_id(id)

    if resultado is None:
        return jsonify({"error": "Utilizador não encontrado"}), NOT_FOUND

    return jsonify(resultado), OK_CODE


#atualizar user
@app.route('/api/users/<int:id>', methods=['PUT'])
def atualizar_utilizador(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Dados em falta"}), BAD_REQUEST_CODE

    # aceita "nome" ou "name"
    nome = data.get("name")
    email = data.get("email")
    password = data.get("password")
    nif = str(data.get("nif") or "").strip()

    if not nome or not email or not password or not nif:
        return jsonify({"error": "Faltam campos obrigatórios"}), BAD_REQUEST_CODE

    if not email_valido(email):
        return jsonify({"error": "Email inválido"}), BAD_REQUEST_CODE

    if not nif_valido(nif):
        return jsonify({"error": "NIF inválido (9 dígitos)"}), BAD_REQUEST_CODE

    resultado = db.atualiza_user(id, nome, email, password, nif)

    if not resultado:
        return jsonify({"error": "Utilizador não encontrado"}), NOT_FOUND

    return jsonify({"message": "Utilizador atualizado com sucesso"}), OK_CODE


#remover user
@app.route('/api/users/<int:id>', methods=['DELETE'])
def remover_utilizador(id):
    resultado = db.remover_utilizador(id)

    if not resultado:
        return jsonify({"error": "Utilizador não encontrado"}), NOT_FOUND

    return jsonify({"message": "Utilizador removido com sucesso"}), OK_CODE

#listar logs
@app.route('/api/logs', methods=['GET'])
def listar_logs():
    resultado = db.lista_logs()

    if resultado is None:
        return jsonify({"error": "Erro ao listar logs"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE


#logs de um user
@app.route('/api/users/<int:id>/logs', methods=['GET'])
def listar_logs_user(id):
    user = db.obter_user_id(id)

    if user is None:
        return jsonify({"error": "Utilizador não encontrado"}), NOT_FOUND

    resultado = db.obter_logs_user(id)

    if resultado is None:
        return jsonify({"error": "Erro ao listar logs do utilizador"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE


#último utilizador com acesso autorizado
@app.route('/api/access/last-authorized', methods=['GET'])
def ultimo_autorizado():
    resultado = db.ultimo_utilizador_autorizado()

    if resultado is None:
        return jsonify({"error": "Ainda não há acessos autorizados"}), NOT_FOUND

    return jsonify(resultado), OK_CODE

@app.route('/api/devices', methods=['POST'])
def adicionar_device():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    nome = data.get("name")
    modelo = data.get("modelo")
    id_alarm_events = data.get("id_alarm_events")

    if not nome or not modelo:
        return jsonify({"error": "Faltam campos obrigatórios (name, modelo)"}), BAD_REQUEST_CODE

    if id_alarm_events is not None:
        try:
            id_alarm_events = int(id_alarm_events)
        except (ValueError, TypeError):
            return jsonify({"error": "id_alarm_events tem de ser um número"}), BAD_REQUEST_CODE

    resultado = db.adiciona_device(nome, modelo, id_alarm_events)

    if resultado is None:
        return jsonify({"error": "Não foi possível adicionar o dispositivo"}), SERVER_ERROR

    return jsonify({
        "message": "Dispositivo adicionado com sucesso",
        "id": resultado
    }), SUCCESS_CODE


#listar devices
@app.route('/api/devices', methods=['GET'])
def listar_devices():
    resultado = db.lista_devices()

    if resultado is None:
        return jsonify({"error": "Erro ao listar dispositivos"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE


#obter device por id
@app.route('/api/devices/<int:id>', methods=['GET'])
def listar_devices_id(id):
    try:
        resultado = db.obter_device_id(id)

        if resultado is None:
            return jsonify({"error": "Device inexistente"}), NOT_FOUND

        return jsonify(resultado), OK_CODE

    except Exception as e:
        print("ERRO NA ROTA DEVICE:", repr(e))
        return jsonify({"error": "Erro interno do servidor"}), SERVER_ERROR


#atualizar device
@app.route('/api/devices/<int:id>', methods=['PUT'])
def atualizar_device(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Dados em falta"}), BAD_REQUEST_CODE

    nome = data.get("name")
    modelo = data.get("modelo")

    if not nome or not modelo:
        return jsonify({"error": "Faltam campos obrigatórios (name, modelo)"}), BAD_REQUEST_CODE

    if "id_alarm_events" in data:
        id_alarm_events = data["id_alarm_events"]

        if id_alarm_events is not None:
            try:
                id_alarm_events = int(id_alarm_events)
            except (ValueError, TypeError):
                return jsonify({"error": "id_alarm_events tem de ser um número"}), BAD_REQUEST_CODE
    else:
        try:
            atual = db.obter_device_id(id)
        except Exception:
            return jsonify({"error": "Erro ao obter o device"}), SERVER_ERROR

        if atual is None:
            return jsonify({"error": "Device não encontrado"}), NOT_FOUND

        id_alarm_events = atual["id_alarm_events"]

    resultado = db.atualiza_device(id, nome, modelo, id_alarm_events)

    if not resultado:
        return jsonify({"error": "Device não encontrado"}), NOT_FOUND

    return jsonify({"message": "Device atualizado com sucesso"}), OK_CODE


#remover device
@app.route('/api/devices/<int:id>', methods=['DELETE'])
def remover_device(id):
    resultado = db.remove_device(id)

    if resultado is None:
        return jsonify({"error": "Erro ao remover o device"}), SERVER_ERROR

    if resultado == "EM_USO":
        return jsonify({"error": "O device tem leituras, alarmes ou comandos associados"}), CONFLICT_CODE

    if not resultado:
        return jsonify({"error": "Device não encontrado"}), NOT_FOUND

    return jsonify({"message": "Device removido com sucesso"}), OK_CODE
    
@app.route('/api/temp_readings', methods=['POST'])
def adicionar_temperatura():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    if "temp_value" not in data or "id_device" not in data:
        return jsonify({"error": "missing parameters"}), BAD_REQUEST_CODE

    try:
        id_device = int(data["id_device"])
        temp_value = float(data["temp_value"])
    except (ValueError, TypeError):
        return jsonify({"error": "id_device e temp_value têm de ser números"}), BAD_REQUEST_CODE

    if not math.isfinite(temp_value) or temp_value < -50 or temp_value > 150:
        return jsonify({"error": "temp_value fora do intervalo válido (-50 a 150)"}), BAD_REQUEST_CODE

    existe = device_existe(id_device)

    if existe is None:
        return jsonify({"error": "Erro ao verificar o device"}), SERVER_ERROR

    if not existe:
        return jsonify({"error": "Device não encontrado"}), NOT_FOUND

    resultado = db.adicionar_temperatura(temp_value, id_device)

    if resultado is None:
        return jsonify({"error": "Não foi possível guardar a temperatura"}), SERVER_ERROR

    if resultado["alarme_disparou"]:
        mensagem = "Temperatura adicionada. Alarme disparado!"
    else:
        mensagem = "Temperatura adicionada com sucesso"

    return jsonify({
        "message": mensagem,
        "alarme_disparou": resultado["alarme_disparou"]
    }), SUCCESS_CODE


#listar leituras
@app.route('/api/temp_readings', methods=['GET'])
def listar_temp_readings():
    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 500))

    resultado = db.lista_temp_readings(limit)

    if resultado is None:
        return jsonify({"error": "Erro ao listar temperaturas"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE


#última leitura de um device
@app.route('/api/devices/<int:id>/temp_readings/latest', methods=['GET'])
def ultima_temperatura(id):
    resultado = db.ultima_temp_device(id)

    if resultado is None:
        return jsonify({"error": "Sem leituras para este device"}), NOT_FOUND

    return jsonify(resultado), OK_CODE


#histórico de um device
@app.route('/api/devices/<int:id>/temp_readings', methods=['GET'])
def historico_temperatura(id):
    data_inicio = request.args.get("from")
    data_fim = request.args.get("to")

    if not data_inicio or not data_fim:
        return jsonify({"error": "Faltam os parâmetros from e to"}), BAD_REQUEST_CODE

    try:
        inicio = datetime.fromisoformat(data_inicio)
        fim = datetime.fromisoformat(data_fim)

        if inicio > fim:
            return jsonify({"error": "'from' tem de ser anterior a 'to'"}), BAD_REQUEST_CODE

    except (ValueError, TypeError):
        return jsonify({"error": "Datas inválidas (usar ISO 8601, ex: 2026-11-25T10:00:00)"}), BAD_REQUEST_CODE

    resultado = db.historico_temp_device(id, data_inicio, data_fim)

    if resultado is None:
        return jsonify({"error": "Erro ao obter histórico"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE

#listar alarmes
@app.route('/api/alarms', methods=['GET'])
def listar_alarmes():
    ativos = request.args.get("active", "false").lower() == "true"

    resultado = db.lista_alarmes(ativos)

    if resultado is None:
        return jsonify({"error": "Erro ao listar alarmes"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE


#alarmes de um device
@app.route('/api/devices/<int:id>/alarms', methods=['GET'])
def listar_alarmes_device(id):
    resultado = db.alarmes_device(id)

    if resultado is None:
        return jsonify({"error": "Erro ao listar alarmes do device"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE


#marcar alarme como resolvido
@app.route('/api/alarms/<int:id>/resolve', methods=['PUT'])
def resolver_alarme(id):
    resultado = db.resolve_alarme(id)

    if not resultado:
        return jsonify({"error": "Alarme não encontrado ou já resolvido"}), NOT_FOUND

    return jsonify({"message": "Alarme resolvido com sucesso"}), OK_CODE


# ======================= COMANDOS =======================

#enviar comando (fan_on, fan_off, alarm_on, alarm_off)
@app.route('/api/commands', methods=['POST'])
def enviar_comando():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    if "id_device" not in data or "command" not in data:
        return jsonify({"error": "missing parameters"}), BAD_REQUEST_CODE

    if data["command"] not in COMANDOS_VALIDOS:
        return jsonify({
            "error": "Comando inválido",
            "validos": COMANDOS_VALIDOS
        }), BAD_REQUEST_CODE

    try:
        id_device = int(data["id_device"])
    except (ValueError, TypeError):
        return jsonify({"error": "id_device tem de ser um número"}), BAD_REQUEST_CODE

    existe = device_existe(id_device)

    if existe is None:
        return jsonify({"error": "Erro ao verificar o device"}), SERVER_ERROR

    if not existe:
        return jsonify({"error": "Device não encontrado"}), NOT_FOUND

    # devolve o id do comando novo, ou None se der erro
    resultado = db.adiciona_comando(id_device, data["command"])

    if resultado is None:
        return jsonify({"error": "Não foi possível enviar o comando"}), SERVER_ERROR

    return jsonify({
        "message": "Comando enviado com sucesso",
        "id": resultado
    }), SUCCESS_CODE


#listar comandos
@app.route('/api/commands', methods=['GET'])
def listar_comandos():
    resultado = db.lista_comandos()

    if resultado is None:
        return jsonify({"error": "Erro ao listar comandos"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE

@app.route('/api/devices/<int:id>/commands/pending', methods=['GET'])
def listar_comandos_pendentes(id):
    resultado = db.comandos_pendentes(id)

    if resultado is None:
        return jsonify({"error": "Erro ao listar comandos pendentes"}), SERVER_ERROR

    return jsonify(resultado), OK_CODE

@app.route('/api/commands/<int:id>/done', methods=['PUT'])
def comando_executado(id):
    resultado = db.marca_comando_feito(id)

    if not resultado:
        return jsonify({"error": "Comando não encontrado ou já executado"}), NOT_FOUND

    return jsonify({"message": "Comando marcado como executado"}), OK_CODE
