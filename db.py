import json
import os
import bcrypt
import psycopg2
from re import I

import psycopg2
def get_connection():
    return psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )

def add_user(nome, email, password, nif):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Hashing da password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        passwordHashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        cursor.execute("SELECT tam.adiciona_user(nome, email, passwordHashed, nif)")

        resultadoAdicionaUser = cursor.fetchone()[0]

        conn.commit()

        cursor.close()

        return resultadoAdicionaUser


    except Exception as e:
        if conn:
            conn.rollback()
        print("ERRO: Erro ao adicionar Utilizador")
        return False

    finally:
        if conn:
            conn.close()
