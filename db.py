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
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        cursor.execute(
            "CALL tam.adiciona_user(%s, %s, %s, %s)",
            (nome, email, password_hash, nif)
        )

        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()

        print("Erro ao adicionar utilizador:", repr(e))
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
