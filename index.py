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
[ ] Listar users                        GET    /api/users
[ ] Obter user por id                   GET    /api/users/<id>
[ ] Atualizar user                      PUT    /api/users/<id>
[ ] Desativar/remover user              DELETE /api/users/<id>

ACCESS LOGS (só consulta, o registo é feito no login)
[ ] Listar logs (filtro status/limit)   GET    /api/logs
[ ] Logs de um user                     GET    /api/users/<id>/logs

DEVICES
[ ] Adicionar device                    POST   /api/devices
[ ] Listar devices                      GET    /api/devices
[ ] Obter device por id                 GET    /api/devices/<id>
[ ] Atualizar device                    PUT    /api/devices/<id>
[ ] Remover device                      DELETE /api/devices/<id>

TEMP READINGS (TMP)
[x] Adicionar valor TMP                 POST   /api/temp_readings
[ ] Listar leituras (limit)             GET    /api/temp_readings
[ ] Última leitura de um device         GET    /api/devices/<id>/temp_readings/latest
[ ] Histórico de um device (de/até)     GET    /api/devices/<id>/temp_readings

ALARM EVENTS
[ ] Listar alarmes                      GET    /api/alarms
[ ] Alarmes de um device                GET    /api/devices/<id>/alarms
[ ] Alarmes ativos/não resolvidos       GET    /api/alarms?active=true
[ ] Marcar alarme como resolvido        PUT    /api/alarms/<id>/resolve

COMMANDS (ativar alarme / ativar ventoinha)
[ ] Enviar comando (ALARM_ON, FAN_ON)   POST   /api/commands
[ ] Listar comandos                     GET    /api/commands
[ ] Comandos pendentes de um device     GET    /api/devices/<id>/commands/pending
[ ] Marcar comando como executado       PUT    /api/commands/<id>/done
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

    if not data or not all(
        campo in data and data[campo]
        for campo in ['name', 'email', 'password', 'nif']
    ):
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
        jsonify({"Erro": "Sem utilizadores para listar"})
    
    return jsonify(resultado), 200

#listar user por id
@app.route('/api/users/<id>', methods=['GET'])
def listar_user_id(id):

    resultado = db.obter_user_id(id)

    if resultado is None:
        jsonify({"Erro": "Utilizador não encontrado"})


    return jsonify(resultado), 200
