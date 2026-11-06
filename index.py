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

#LOGIN  
@app.route('/api/door/unlock', methods=['POST'])
def login():
    data = request.get_json()
    
   
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Parâmetros inválidos"}), BAD_REQUEST_CODE

    user = db.adiciona_log(data['email'], data["password"])

       
    if isinstance(user, str):
        return jsonify({"error": "Erro interno", "details": user}), SERVER_ERROR

    
    if user is None:
        return jsonify({"error": "Credenciais incorretas"}), BAD_REQUEST_CODE

    
    token = jwt.encode({
        'user_id': user['id'],  
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30)   #Tem que se particionar por dia na tabela
    }, app.config['SECRET_KEY'], algorithm='HS256')

    user["token"] = token
    return jsonify(user), SUCCESS_CODE

#REGISTER
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)

    if not data or not all(
        campo in data
        for campo in ['username', 'email', 'password', 'nif']
    ):
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    resultado = db.add_user(
        data['username'],
        data['email'],
        data['password'],
        data['nif']
    )

    if resultado is True:
        return jsonify({
            "message": "User created"
        }), SUCCESS_CODE

    return jsonify({
        "error": "Registration failed"
    }), 500

#ADICIONAR LEITURA SENSOR TMP

@app.route('/api/telemetry', methods=['POST'])

def registar_leitura_tmp():

    data = request.get_json()

    if not data:
        return jsonify({"error: no parameters received"}), 400

    temperatura_adicionada = db.adiciona_leitura_tmp(data["temperature_value"]) #Aqui a db.py deve receber temp value e chamar a funcao para adicionar a temperatura. Essa função deve guardar o valor na bd.



    
