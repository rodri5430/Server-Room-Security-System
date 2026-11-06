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
    return adiciona_user(nome, email, password, nif)
