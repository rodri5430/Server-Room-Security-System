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
@app.route('api/logs/', methods=['POST'])

def adicionar_log():
    data = request.get_json()

    if not data.get("email") or not data.get("password_hash"):
        return jsonify({"error": "falta de dados obrigatórios"}), 400

    resultado = db.adiciona_logs(data["email"], data["password_hash"])

    if resultado is None:
        return jsonify({"error": "Erro interno ao registar log"}), 500

    if not resultado["sucesso"]:
        return jsonify({"error": resultado["mensagem"]}), 401

    return jsonify({
        "status": "ok",
        "user_id": resultado["user_id"],
        "user_nome": resultado["user_nome"],
        "mensagem": resultado["mensagem"]
    }), 200

    
