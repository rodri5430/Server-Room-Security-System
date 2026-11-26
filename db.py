#db.py
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

#Login + registo do log
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

#listar utilizadores

def lista_users():

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tam.fn_get_users()")

        resultado = cursor.fetchall()

        utilizadores = []


        for row in resultado:
            utilizadores.append({
                "id": row[0],
                "nome": row[1],
                "email": row[2]
            })

        return utilizadores

    except Exception as e:
        if conn:
            conn.rollback()
        print("ERRO NA LISTAGEM DE UTILIZADORES:", repr(e))
        return None
    
    finally:
        if conn:
            conn.close()

def atualiza_user(id, nome, email, password, nif):

    conn = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # Hashing da password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        passwordHashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        cursor.execute('SELECT tam.fn_atualiza_user(%s, %s, %s, %s, %s)', (id, nome, email, passwordHashed, nif))


        resultado = cursor.fetchone()[0]

        conn.commit()

        return resultado

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO AO ATUALIZAR UTILIZADOR:", repr(e))
        return False
    finally:
        if conn:
            conn.close()

def remover_utilizador(id):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT tam.fn_remove_utilizador(%s)', (id,))

        resultado = cursor.fetchone()[0]

        conn.commit()

        return resultado
    except Exception as e:

        if conn:
            conn.rollback()

        print("ERRO AO ELIMINAR UTILIZADOR: ", repr(e))
        return False
    finally:
        if conn:
            conn.close()

def adiciona_device(nome, modelo, id_alarme):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT tam.adiciona_device(%s, %s, %s)',
            (nome, modelo, id_alarme)
        )

        resultado = cursor.fetchone()[0]
        conn.commit()

        if not resultado:
            return None

        return resultado

    except Exception as e:

        if conn:
            conn.rollback()

        print("ERRO AO ADICIONAR DEVICE:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#obter user por id
def obter_user_id(user_id):

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, nome, email, nif FROM tam.fn_user_search_id(%s)', (user_id,))

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return {
            "id": resultado[0],
            "nome": resultado[1],
            "email": resultado[2],
            "nif": resultado[3]
        }

    except Exception as e:
        print("ERRO NA LISTAGEM DO UTILIZADOR:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#logs de um user
def obter_logs_user(id):

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT log_id, login_time, status FROM tam.fn_logs_search_id(%s)', (id,))

        resultado = cursor.fetchall()

        logs = []

        for row in resultado:
            logs.append({
                "log_id": row[0],
                "login_time": row[1],
                "status": row[2]
            })

        return logs

    except Exception as e:
        print("ERRO NA LISTAGEM DOS LOGS DO UTILIZADOR:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#listar logs
def lista_logs():

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tam.fn_get_access_logs()')

        resultado = cursor.fetchall()

        logs = []

        for row in resultado:
            logs.append({
                "log_id": row[0],
                "utilizador_nome": row[1],
                "utilizador_email": row[2],
                "login_time": row[3],
                "status": row[4]
            })

        return logs

    except Exception as e:
        print("ERRO NA LISTAGEM DOS LOGS:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#listar devices
def lista_devices():

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tam.fn_list_devices()')

        resultado = cursor.fetchall()

        devices = []

        for row in resultado:
            devices.append({
                "id": row[0],
                "name": row[1],
                "model": row[2],
                "id_alarm_events": row[3]
            })

        return devices

    except Exception as e:
        print("ERRO NA LISTAGEM DOS DEVICES:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#adicionar temperatura
def adicionar_temperatura(temp_value, id_device):

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT tam.fn_processo_leitura_temperatura(%s, %s)',
            (id_device, temp_value)
        )

        alarme_disparou = cursor.fetchone()[0]

        conn.commit()

        return {"alarme_disparou": alarme_disparou}

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO AO ADICIONAR TEMPERATURA:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#NOVA: último utilizador com acesso autorizado
def ultimo_utilizador_autorizado():

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tam.fn_obter_ultimo_utilizador_autorizado()')

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return {
            "nome_utilizador": resultado[0],
            "email_utilizador": resultado[1],
            "data_hora_acesso": resultado[2]
        }

    except Exception as e:
        print("ERRO NO ÚLTIMO UTILIZADOR AUTORIZADO:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#obter device por id (substitui a versão anterior)
def obter_device_id(id_device):
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tam.fn_list_devices_id(%s)",
            (id_device,)
        )

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return {
            "id": resultado[0],
            "name": resultado[1],
            "model": resultado[2],
            "id_alarm_events": resultado[3]
        }

    except Exception as e:
        print("ERRO REAL NA CONSULTA DO DEVICE:", repr(e))
        raise

    finally:
        if conn:
            conn.close()

#atualizar device
def atualiza_device(id_device, nome, modelo, id_alarme):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT tam.fn_update_device(%s, %s, %s, %s)',
            (id_device, nome, modelo, id_alarme)
        )

        resultado = cursor.fetchone()[0]

        conn.commit()

        return resultado

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO AO ATUALIZAR DEVICE:", repr(e))
        return False

    finally:
        if conn:
            conn.close()

#remover device
def remove_device(id_device):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT tam.fn_remove_device(%s)', (id_device,))

        resultado = cursor.fetchone()[0]

        conn.commit()

        return resultado

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO AO REMOVER DEVICE:", repr(e))
        return False

    finally:
        if conn:
            conn.close()

#listar leituras de temperatura (com limit)
def lista_temp_readings(limit):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id_device, temperature_value, recorded_at FROM tam.fn_list_temp_readings(%s)', (limit,))

        resultado = cursor.fetchall()

        leituras = []

        for row in resultado:
            leituras.append({
                "id_device": row[0],
                "temperature_value": float(row[1]),
                "recorded_at": row[2]
            })

        return leituras

    except Exception as e:
        print("ERRO NA LISTAGEM DAS TEMPERATURAS:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#última leitura de um device
def ultima_temp_device(id_device):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id_device, temperature_value, recorded_at FROM tam.fn_latest_temp_reading(%s)',
            (id_device,)
        )

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return {
            "id_device": resultado[0],
            "temperature_value": float(resultado[1]),
            "recorded_at": resultado[2]
        }

    except Exception as e:
        print("ERRO NA ÚLTIMA TEMPERATURA:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#histórico de um device (de/até)
def historico_temp_device(id_device, data_inicio, data_fim):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id_device, temperature_value, recorded_at FROM tam.fn_temp_readings_by_device(%s, %s, %s)',
            (id_device, data_inicio, data_fim)
        )

        resultado = cursor.fetchall()

        leituras = []

        for row in resultado:
            leituras.append({
                "id_device": row[0],
                "temperature_value": float(row[1]),
                "recorded_at": row[2]
            })

        return leituras

    except Exception as e:
        print("ERRO NO HISTÓRICO DE TEMPERATURAS:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#listar alarmes (ativos = só os não resolvidos)
def lista_alarmes(ativos):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, id_device, trigger_reason, resolved_at FROM tam.fn_list_alarms(%s)', (ativos,))

        resultado = cursor.fetchall()

        alarmes = []

        for row in resultado:
            alarmes.append({
                "id": row[0],
                "id_device": row[1],
                "trigger_reason": row[2],
                "resolved_at": row[3]
            })

        return alarmes

    except Exception as e:
        print("ERRO NA LISTAGEM DOS ALARMES:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#alarmes de um device
def alarmes_device(id_device):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, id_device, trigger_reason, resolved_at FROM tam.fn_alarms_by_device(%s)', (id_device,))

        resultado = cursor.fetchall()

        alarmes = []

        for row in resultado:
            alarmes.append({
                "id": row[0],
                "id_device": row[1],
                "trigger_reason": row[2],
                "resolved_at": row[3]
            })

        return alarmes

    except Exception as e:
        print("ERRO NOS ALARMES DO DEVICE:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#marcar alarme como resolvido
def resolve_alarme(id_alarme):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT tam.fn_resolve_alarm(%s)', (id_alarme,))

        resultado = cursor.fetchone()[0]

        conn.commit()

        return resultado

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO AO RESOLVER ALARME:", repr(e))
        return False

    finally:
        if conn:
            conn.close()

#enviar comando
def adiciona_comando(id_device, comando):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT tam.fn_add_command(%s, %s)', (id_device, comando))

        resultado = cursor.fetchone()[0]

        conn.commit()

        return resultado

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO AO ADICIONAR COMANDO:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#listar comandos
def lista_comandos():

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, id_device, command_text, executed FROM tam.fn_list_commands()')

        resultado = cursor.fetchall()

        comandos = []

        for row in resultado:
            comandos.append({
                "id": row[0],
                "id_device": row[1],
                "command_text": row[2],
                "executed": row[3]
            })

        return comandos

    except Exception as e:
        print("ERRO NA LISTAGEM DOS COMANDOS:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#comandos pendentes de um device
def comandos_pendentes(id_device):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, id_device, command_text, executed FROM tam.fn_pending_commands(%s)', (id_device,))

        resultado = cursor.fetchall()

        comandos = []

        for row in resultado:
            comandos.append({
                "id": row[0],
                "id_device": row[1],
                "command_text": row[2],
                "executed": row[3]
            })

        return comandos

    except Exception as e:
        print("ERRO NOS COMANDOS PENDENTES:", repr(e))
        return None

    finally:
        if conn:
            conn.close()

#marcar comando como executado
def marca_comando_feito(id_comando):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT tam.fn_mark_command_done(%s)', (id_comando,))

        resultado = cursor.fetchone()[0]

        conn.commit()

        return resultado

    except Exception as e:
        if conn:
            conn.rollback()

        print("ERRO AO MARCAR COMANDO COMO EXECUTADO:", repr(e))
        return False

    finally:
        if conn:
            conn.close()
