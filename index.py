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
   return "Olá, Utilizador"

#LOGIN  
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
   
    if not data or "nome" not in data or "password" not in data:
        return jsonify({"error": "Parâmetros inválidos"}), 400

    user = db.login(data['nome'], data["password"])

    
    if isinstance(user, str):
        return jsonify({"error": "Erro interno", "details": user}), 500

    
    if user is None:
        return jsonify({"error": "Credenciais incorretas"}), 401

    
    token = jwt.encode({
        'user_id': user['id'], 
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    user["token"] = token
    return jsonify(user), 200

#REGISTER
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data or "email" not in data:
        return jsonify({"error": "invalid parameters"}), 400

    if db.user_exists(data['username']):
        return jsonify({"error": "user already exists"}), 400
       
    user_id = db.add_user(data['username'], data['email'], data['password'])

    if isinstance(user_id, int):
        return jsonify({"message": "User created", "id": user_id}), 201
    else:
        return jsonify({"error": "Registration failed", "details": user_id}), BAD_REQUEST