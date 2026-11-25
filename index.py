#index.py

import os
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request
import jwt
import db

'''
AUTH / USERS
[x] Adicionar user                      POST   /api/auth/register
[x] Login + registo do log              POST   /api/auth/login
[x] Listar users                        GET    /api/users
[x] Obter user por id                   GET    /api/users/<id>
[x] Atualizar user                      PUT    /api/users/<id>
[x] Desativar/remover user              DELETE /api/users/<id>

ACCESS LOGS (só consulta, o registo é feito no login)
[x] Listar logs                         GET    /api/logs
[x] Logs de um user                     GET    /api/users/<id>/logs

DEVICES
[x] Adicionar device                    POST   /api/devices
[x] Listar devices                      GET    /api/devices
[ ] Obter device por id                 GET    /api/devices/<id>
[x] Atualizar device                    PUT    /api/devices/<id>
[x] Remover device                      DELETE /api/devices/<id>

TEMP READINGS (TMP)
[x] Adicionar valor TMP                 POST   /api/temp_readings
[x] Listar leituras (limit)             GET    /api/temp_readings
[x] Última leitura de um device         GET    /api/devices/<id>/temp_readings/latest
[ ] Histórico de um device (de/até)     GET    /api/devices/<id>/temp_readings

ALARM EVENTS
[x] Listar alarmes                      GET    /api/alarms
[x] Alarmes de um device                GET    /api/devices/<id>/alarms
[x] Alarmes ativos/não resolvidos       GET    /api/alarms?active=true
[x] Marcar alarme como resolvido        PUT    /api/alarms/<id>/resolve

COMMANDS (ativar alarme / ativar ventoinha)
[x] Enviar comando                      POST   /api/commands
[x] Listar comandos                     GET    /api/commands
[x] Comandos pendentes de um device     GET    /api/devices/<id>/commands/pending
[x] Marcar comando como executado       PUT    /api/commands/<id>/done
'''

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')

NOT_FOUND_CODE = 401
OK_CODE = 200
SUCCESS_CODE = 201
NO_CONTENT_CODE = 204
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN_CODE = 403
NOT_FOUND = 404
SERVER_ERROR = 500


#PAGINA ENTRADA
@app.route('/', methods = ["GET"])
def home():
   return "Bem-Vindo à Sala de Servidores da ESTGOH"
   
#REGISTER
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "invalid parameters"
        }), BAD_REQUEST_CODE

    try:
        resultado = db.add_user(
            data['name'],
            data['email'],
            data['password'],
            data['nif']
        )

        if resultado == 'SUCESSO':
            return jsonify({
            "message": "utilizador adicionado com sucesso"
            }), 201

        elif resultado == 'EMAIL_EXISTE':
            return jsonify({
                "error": "Email já registado"
            }), 409

        elif resultado == 'NIF_EXISTE':
            return jsonify({
                "error": "NIF já registado"
            }), 409

    except Exception as e:
        print("Erro no registo:", repr(e))

        return jsonify({
            "error": "Internal server error"
        }), SERVER_ERROR


#Adicionar Log
@app.route('/api/auth/login', methods=['POST'])
def adicionar_log():

    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Falta de dados obrigatórios"}), 400

    resultado = db.adiciona_logs(data["email"], data["password"])

    if resultado is None:
        return jsonify({"error": "Erro interno ao iniciar sessão"}), 500

    if not resultado["sucesso"]:
        return jsonify({"error": resultado["mensagem"]}), 401

    return jsonify(resultado), 200

#listar users 
@app.route('/api/users')
def listar_users():

    resultado = db.lista_users()

    if resultado is None:
        return jsonify({"Erro": "Sem utilizadores para listar"})
    
    return jsonify(resultado), 200

#listar user por id
@app.route('/api/users/<id>', methods=['GET'])
def listar_user_id(id):

    resultado = db.obter_user_id(id)

    if resultado is None:
        return jsonify({"Erro": "Utilizador não encontrado"})

    return jsonify(resultado), 200

#atualizar utilizador
@app.route('/api/users/<id>', methods=['PUT'])
def atualizar_utilizador(id):

    data = request.get_json()

    if not data:
        return jsonify({"error": "Dados em falta"}), 400

    nome = data.get("nome")
    email = data.get("email")
    password = data.get("password")
    nif = data.get("nif")

    if not nome or not email or not password or not nif:
        return jsonify({"error": "Faltam campos obrigatórios"}), 400

    resultado = db.atualiza_user(id, nome, email, password, nif)

    if not resultado:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    return jsonify({"mensagem": "Utilizador atualizado com sucesso"}), 200

#Remover utilizador

@app.route('/api/users/<id>', methods=['DELETE'])

def remover_utilizador(id):

    resultado = db.remover_utilizador(id)

    if not resultado:
        return jsonify({"mensagem": "Utilizador não encontrado"}), 404


    return jsonify({"mensagem": "Utilizador Removido com Sucesso"}), 200

#Listar Logs
@app.route('/api/logs', methods=['GET'])
def listar_logs():
    
    resultado = db.lista_users()

    if resultado is None:
        return jsonify({"Erro": "Sem logs para listar"})
    
    return jsonify(resultado), 200

#listar logs por id
@app.route('/api/users/<id>/logs', methods=['GET'])

def listar_logs_user(id):
    resultado = db.obter_logs_user(id)
    
    if resultado is None:
        return jsonify({"Erro": "Sem Logs para o utilizador"})
    
    return jsonify(resultado), 200

#Adicionar Dispositivo
@app.route('/api/devices', methods=['POST'])

def adicionar_device():
    data = request.get_json()


    if not data: 
        return jsonify({
            "error": "invalid parameters"
        }), BAD_REQUEST_CODE

    resultado = db.adiciona_device(data["id"], data["name"], data["modelo"], data["id_alarm_events"])

    if resultado:
        return jsonify({
        "message": "Dispositivo Adicionado com Sucesso"
        }), 201
    
    return jsonify({
        "error": "Não foi possível adicionar Dispositivos"
    }), 400

#listar devices
@app.route('/api/devices', methods=['GET']) 
def listar_devices():
   
    resultado = db.lista_devices()

    if resultado is None:
        return jsonify({"Erro": "Sem logs para listar"})
    
    return jsonify(resultado), 200 

@app.route('/api/devices/<id>', methods=['GET'])
def listar_devices_id(id):

    try:
        resultado = db.obter_device_id(id)

        if resultado is None:
            return jsonify({"Erro": "Device Inexistente"}), 404

        return jsonify(resultado), 200

    except Exception as e:
        print("ERRO NA ROTA DEVICE:", repr(e))
        return jsonify({"Erro": "Erro interno do servidor"}), 500
       
#Adicionar temperatura
@app.route('/api/temp_readings', methods=['POST'])
def adicionar_temperatura():

    data = request.get_json()

    if not data: 
        return jsonify({
            "error": "invalid parameters"
        }), BAD_REQUEST_CODE
    
    if "temp_value" not in data or "id_device" not in data:
        return jsonify({
            "error": "missing parameters"
        }), BAD_REQUEST_CODE
    
    resultado = db.adicionar_temperatura(
            data["temp_value"],
            data["id_device"]
        )
    
    return jsonify({
            "message": "Temperatura adicionada com sucesso",
            "resultado": resultado
        }), 201

#Atualizar device
@app.route('/api/devices/<id>', methods=['PUT'])
def atualizar_device(id):

    data = request.get_json()

    if not data:
        return jsonify({"error": "Dados em falta"}), 400

    nome = data.get("name")
    modelo = data.get("modelo")
    id_alarm_events = data.get("id_alarm_events")

    if not nome or not modelo or id_alarm_events is None:
        return jsonify({"error": "Faltam campos obrigatórios"}), 400

    resultado = db.atualiza_device(id, nome, modelo, id_alarm_events)

    if not resultado:
        return jsonify({"error": "Device não encontrado"}), 404

    return jsonify({"mensagem": "Device atualizado com sucesso"}), 200

#Remover device
@app.route('/api/devices/<id>', methods=['DELETE'])
def remover_device(id):

    resultado = db.remove_device(id)

    if not resultado:
        return jsonify({"mensagem": "Device não encontrado"}), 404

    return jsonify({"mensagem": "Device removido com sucesso"}), 200

#Listar leituras de temperatura (?limit=50)
@app.route('/api/temp_readings', methods=['GET'])
def listar_temp_readings():

    limit = request.args.get("limit", default=50, type=int)

    resultado = db.lista_temp_readings(limit)

    if resultado is None:
        return jsonify({"Erro": "Erro ao listar temperaturas"}), 500

    return jsonify(resultado), 200

#Última leitura de um device
@app.route('/api/devices/<id>/temp_readings/latest', methods=['GET'])
def ultima_temperatura(id):

    resultado = db.ultima_temp_device(id)

    if resultado is None:
        return jsonify({"Erro": "Sem leituras para este device"}), 404

    return jsonify(resultado), 200

#Histórico de um device (?from=2026-11-25T00:00:00&to=2026-11-25T23:59:59)
@app.route('/api/devices/<id>/temp_readings', methods=['GET'])
def historico_temperatura(id):

    data_inicio = request.args.get("from")
    data_fim = request.args.get("to")

    if not data_inicio or not data_fim:
        return jsonify({"error": "Faltam os parâmetros from e to"}), 400 

    resultado = db.historico_temp_device(id, data_inicio, data_fim)

    if resultado is None:
        return jsonify({"Erro": "Erro ao obter histórico"}), 500

    return jsonify(resultado), 200

#Listar alarmes (?active=true para só os não resolvidos)
@app.route('/api/alarms', methods=['GET'])
def listar_alarmes():

    ativos = request.args.get("active", "false").lower() == "true"

    resultado = db.lista_alarmes(ativos)

    if resultado is None:
        return jsonify({"Erro": "Erro ao listar alarmes"}), 500

    return jsonify(resultado), 200

#Alarmes de um device
@app.route('/api/devices/<id>/alarms', methods=['GET'])
def listar_alarmes_device(id):

    resultado = db.alarmes_device(id)

    if resultado is None:
        return jsonify({"Erro": "Erro ao listar alarmes do device"}), 500

    return jsonify(resultado), 200

#Marcar alarme como resolvido
@app.route('/api/alarms/<id>/resolve', methods=['PUT'])
def resolver_alarme(id):

    resultado = db.resolve_alarme(id)

    if not resultado:
        return jsonify({"error": "Alarme não encontrado ou já resolvido"}), 404

    return jsonify({"mensagem": "Alarme resolvido com sucesso"}), 200

#Enviar comando (fan_on, fan_off, alarm_on, alarm_off)
@app.route('/api/commands', methods=['POST'])
def enviar_comando():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "invalid parameters"
        }), BAD_REQUEST_CODE

    if "id_device" not in data or "command" not in data:
        return jsonify({
            "error": "missing parameters"
        }), BAD_REQUEST_CODE

    if data["command"] not in ["fan_on", "fan_off", "alarm_on", "alarm_off"]:
        return jsonify({
            "error": "Comando inválido"
        }), BAD_REQUEST_CODE

    resultado = db.adiciona_comando(data["id_device"], data["command"])

    if resultado is None:
        return jsonify({"error": "Não foi possível enviar o comando"}), 500

    return jsonify({
        "message": "Comando enviado com sucesso",
        "id": resultado
    }), 201

#Listar comandos
@app.route('/api/commands', methods=['GET'])
def listar_comandos():

    resultado = db.lista_comandos()

    if resultado is None:
        return jsonify({"Erro": "Erro ao listar comandos"}), 500

    return jsonify(resultado), 200

#Comandos pendentes de um device
@app.route('/api/devices/<id>/commands/pending', methods=['GET'])
def listar_comandos_pendentes(id):

    resultado = db.comandos_pendentes(id)

    if resultado is None:
        return jsonify({"Erro": "Erro ao listar comandos pendentes"}), 500

    return jsonify(resultado), 200

#Marcar comando como executado
@app.route('/api/commands/<id>/done', methods=['PUT'])
def comando_executado(id):

    resultado = db.marca_comando_feito(id)

    if not resultado:
        return jsonify({"error": "Comando não encontrado ou já executado"}), 404

    return jsonify({"mensagem": "Comando marcado como executado"}), 200
