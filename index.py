import os
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request
import jwt
import db

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

#POST     /api/door/unlock       Validar a palavra-passe e solicitar abertura da porta
#GET     /api/fan/status        Consultar o estado da ventoinha
#POST     /api/fan/control        Ligar ou desligar a ventoinha manualmente
#POST     /api/fan/mode            Selecionar modo automático ou manual
#POST     /api/alarm/activate         Ativar o alarme
#POST     /api/alarm/deactivate        Desativar o alarme
#GET     /api/alarm/status        Consultar o estado e os detalhes do alarme
#GET     /api/telemetry/latest        Obter a última leitura dos sensores
#GET     /api/telemetry/history        Consultar o histórico dos sensores
#GET     /api/devices/commands/pending    O ESP32 consulta comandos pendentes
#POST     /api/devices/commands/ack    O ESP32 confirma a execução dos comandos
#GET     /api/access-logs        Consultar o histórico de entradas
#GET     /api/alerts            Consultar os alertas registados

#PAGINA ENTRADA
@app.route('/', methods = ["GET"])
def home():
   return "Bem-Vindo à Sala de Servidores da ESTGOH"
   
#REGISTER

# REGISTER
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)

    if not data or not all(
        campo in data and data[campo]
        for campo in ['name', 'email', 'password', 'nif', 'pin_code']
    ):
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    try:
        resultado = db.add_user(
            data['nif'],
            data['name'],
            data['email'],
            data['password'],
            data['pin_code']
        )

        if resultado is True:
            return jsonify({
                "message": "utilizador adicionado com sucesso"
            }), SUCCESS_CODE

        return jsonify({
            "error": "Email ou NIF já registado"
        }), 409

    except Exception as e:
        print("Erro no registo:", repr(e))
        return jsonify({
            "error": "Internal server error"
        }), SERVER_ERROR
