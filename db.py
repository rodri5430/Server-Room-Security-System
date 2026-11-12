import os
import bcrypt
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )



#MÉTODOS ADICIONAR À BD

#Adicionar Utilizador à aplicação
def add_user(nome, email, password, nif):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Hashing da password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        passwordHashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        cursor.execute(
        "SELECT tam.fn_register_user(%s, %s, %s, %s)",
        (nif, nome, email, passwordHashed)
        )
    
        resultadoAdicionaUser = cursor.fetchone()[0]

        print("RESULTADO:", resultadoAdicionaUser)

        conn.commit()

        return resultadoAdicionaUser


    except Exception as e:
        if conn:
            conn.rollback()
        print("ERRO: Erro ao adicionar Utilizador")
        return False

    finally:
        if conn:
            conn.close()

#Adicionar Logs NÃO TEM FUNÇÃO NA BASE DE DADOS 


def adiciona_logs(email, password):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password_hash
            FROM tam.users
            WHERE email = %s
        """, (email,))

        resultado = cursor.fetchone()

        if resultado is None:
            # Email inexistente: registar tentativa falhada
            cursor.execute("""
                SELECT * FROM tam.fn_validacao_e_acesso_log(%s, %s)
            """, (email, ""))

        else:
            password_hash = resultado[0]

            if bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            ): #Se password hashed for igual então adiciona na tabela logs 

                cursor.execute("""
                    SELECT * FROM tam.fn_validacao_e_acesso_log(%s, %s)
                """, (email, password_hash))

            else:
               
                cursor.execute("""
                    SELECT * FROM tam.fn_validacao_e_acesso_log(%s, %s)
                """, (email, ""))

        sucesso, user_id, user_nome, mensagem = cursor.fetchone()

        conn.commit()

        return {
            "sucesso": sucesso,
            "user_id": user_id,
            "user_nome": user_nome,
            "mensagem": mensagem
        }

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO NO LOGIN:", repr(e))
        return None

    finally:
        if conn:
            conn.close()
