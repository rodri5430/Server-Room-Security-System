-- Adicionar Utilizador
CREATE OR REPLACE FUNCTION tam.fn_register_user(
    p_nif VARCHAR(9),
    p_nome VARCHAR(100),
    p_email VARCHAR(100),
    p_password_hash VARCHAR(255)
)
RETURNS TEXT AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM tam.users WHERE email = p_email) THEN
        RETURN 'EMAIL_EXISTE';
    END IF;

    IF EXISTS (SELECT 1 FROM tam.users WHERE nif = p_nif) THEN
        RETURN 'NIF_EXISTE';
    END IF;

    INSERT INTO tam.users (nif, nome, email, password_hash)
    VALUES (p_nif, p_nome, p_email, p_password_hash);

    RETURN 'SUCESSO';
END;
$$ LANGUAGE plpgsql;

-- login
CREATE OR REPLACE FUNCTION tam.fn_validacao_e_acesso_log(
    p_email VARCHAR(100),
    p_password_hash VARCHAR(255)
)
RETURNS TABLE(
    sucesso BOOLEAN,
    user_id INT,
    user_nome VARCHAR(100),
    mensagem TEXT
) AS $$
DECLARE
    v_user RECORD;
BEGIN
    SELECT u.id, u.nome, u.password_hash INTO v_user
    FROM tam.users u
    WHERE u.email = p_email;

    IF NOT FOUND THEN
        INSERT INTO tam.access_logs (id_user, status)
        VALUES (NULL, 'failed');

        sucesso := FALSE;
        mensagem := 'Credenciais invalidas';
        RETURN NEXT;
        RETURN;
    END IF;

    IF v_user.password_hash = p_password_hash THEN
        INSERT INTO tam.access_logs (id_user, status)
        VALUES (v_user.id, 'success');

        sucesso := TRUE;
        user_id := v_user.id;
        user_nome := v_user.nome;
        mensagem := 'Acesso autorizado com sucesso';
        RETURN NEXT;
        RETURN;
    END IF;

    INSERT INTO tam.access_logs (id_user, status)
    VALUES (v_user.id, 'failed');
    sucesso := FALSE;
    mensagem := 'Credenciais invalidas';
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- listar utilizadores
CREATE OR REPLACE FUNCTION tam.fn_get_users()
RETURNS TABLE (
    id INT,
    nome VARCHAR(100),
    email VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.nome, u.email
    FROM tam.users u
    ORDER BY u.id;
END;
$$ LANGUAGE plpgsql;

-- Pesquisar user por id 
CREATE OR REPLACE FUNCTION tam.fn_user_search_id(
    p_user_id INT
)
RETURNS TABLE (
    id INT,
    nome VARCHAR,
    email VARCHAR,
    nif VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.nome,
        u.email,
        u.nif
    FROM tam.users u
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Atualiza Utilizador
CREATE OR REPLACE FUNCTION tam.fn_remove_utilizador(
    p_user_id INT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE tam.access_logs SET id_user = NULL WHERE id_user = p_user_id;
    UPDATE tam.commands SET id_users = NULL WHERE id_users = p_user_id;

    DELETE FROM tam.users WHERE id = p_user_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Remove utilizador
CREATE OR REPLACE FUNCTION tam.fn_remove_utilizador(
    p_user_id INT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE tam.access_logs SET id_user = NULL WHERE id_user = p_user_id;
	
    DELETE FROM tam.users WHERE id = p_user_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

/*LOGS*/

-- Listar Logs
CREATE OR REPLACE FUNCTION tam.fn_get_access_logs()
RETURNS TABLE (
    log_id INT,
    utilizador_nome VARCHAR(100),
    utilizador_email VARCHAR(100),
    login_time TIMESTAMP,
    status VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT a.id, u.nome, u.email, a.login_time, a.status
    FROM tam.access_logs a
    LEFT JOIN tam.users u ON a.id_user = u.id
    ORDER BY a.login_time DESC;
END;
$$ LANGUAGE plpgsql;

-- Listar Logs por Utilizador
CREATE OR REPLACE FUNCTION tam.fn_logs_search_id(
    p_user_id INT
)
RETURNS TABLE (
    log_id INT,
    login_time TIMESTAMP,
    status VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.login_time,
        a.status
    FROM tam.access_logs a
    WHERE a.id_user = p_user_id
    ORDER BY a.login_time DESC;
END;
$$ LANGUAGE plpgsql;

-- Utilizador com ultimo acesso à sala
CREATE OR REPLACE FUNCTION tam.fn_obter_ultimo_utilizador_autorizado()
RETURNS TABLE(
    nome_utilizador VARCHAR(100),
    email_utilizador VARCHAR(100),
    data_hora_acesso TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.nome, u.email, a.login_time
    FROM tam.access_logs a
    JOIN tam.users u ON a.id_user = u.id
    WHERE a.status = 'success'
    ORDER BY a.login_time DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- listar devices
CREATE OR REPLACE FUNCTION tam.fn_list_devices()
RETURNS SETOF tam.devices AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tam.devices ORDER BY id;
END;

-- obter device por id
CREATE OR REPLACE FUNCTION tam.fn_list_devices_id(
    p_id INT
)
RETURNS SETOF tam.devices AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tam.devices WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

-- Atualizar device
CREATE OR REPLACE FUNCTION tam.fn_update_device(
    p_id_device INT,
    p_name VARCHAR(100),
    p_modelo VARCHAR(100),
    p_id_alarm_events INT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE tam.devices
    SET name = p_name,
        model = p_modelo,
        id_alarm_events = p_id_alarm_events
    WHERE id = p_id_device;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Remover device
CREATE OR REPLACE FUNCTION tam.fn_remove_device(
    p_id_device INT
)
RETURNS BOOLEAN AS $$
BEGIN
    DELETE FROM tam.devices WHERE id = p_id_device;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Adicionar Temperatura no sensor 
CREATE OR REPLACE FUNCTION tam.fn_processo_leitura_temperatura(
    p_id_device INT,
    p_temperature NUMERIC
)
RETURNS BOOLEAN AS $$
DECLARE
    limite_maximo NUMERIC := 30.00;
    ja_tem_alarme BOOLEAN;
    alarme_disparou BOOLEAN := FALSE;
BEGIN
    IF p_id_device IS NULL OR p_temperature IS NULL THEN
        RAISE EXCEPTION 'ID do dispositivo ou temperatura não podem ser nulos!';
    END IF;

    INSERT INTO tam.temp_readings (id_device, temperature_value)
    VALUES (p_id_device, p_temperature);

    IF p_temperature > limite_maximo THEN

        SELECT EXISTS (
            SELECT 1
            FROM tam.alarm_events
            WHERE id_device = p_id_device
              AND resolved_at IS NULL
        ) INTO ja_tem_alarme;

        IF NOT ja_tem_alarme THEN
            INSERT INTO tam.alarm_events (id_device, trigger_reason)
            VALUES (p_id_device, 'HIGH_TEMPERATURE');

            alarme_disparou := TRUE;
        END IF;

    END IF;

    RETURN alarme_disparou;
END;
$$ LANGUAGE plpgsql;

-- Últimas leituras (todo os devices)
CREATE OR REPLACE FUNCTION tam.fn_list_temp_readings(
    p_limit INT DEFAULT 50
)
RETURNS SETOF tam.temp_readings AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tam.temp_readings
    ORDER BY recorded_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Histórico de um device entre duas datas
CREATE OR REPLACE FUNCTION tam.fn_temp_readings_by_device(
    p_id_device INT,
    p_inicio TIMESTAMPTZ,
    p_fim TIMESTAMPTZ
)
RETURNS SETOF tam.temp_readings AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tam.temp_readings
    WHERE id_device = p_id_device
      AND recorded_at BETWEEN p_inicio AND p_fim
    ORDER BY recorded_at;
END;
$$ LANGUAGE plpgsql;

-- Alarmes de um device
CREATE OR REPLACE FUNCTION tam.fn_alarms_by_device(
    p_id_device INT
)
RETURNS SETOF tam.alarm_events AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tam.alarm_events
    WHERE id_device = p_id_device
    ORDER BY id DESC;
END;
$$ LANGUAGE plpgsql;

-- Resolver alarme
CREATE OR REPLACE FUNCTION tam.fn_resolve_alarm(
    p_id_alarm INT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE tam.alarm_events
    SET resolved_at = CURRENT_TIMESTAMP
    WHERE id = p_id_alarm
      AND resolved_at IS NULL;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Desativar todos os alarmes ativos de um device
CREATE OR REPLACE FUNCTION tam.fn_desativa_alarme(
    p_id_device INT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE tam.alarm_events
    SET resolved_at = CURRENT_TIMESTAMP
    WHERE id_device = p_id_device
      AND resolved_at IS NULL;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Enviar comando a um device
CREATE OR REPLACE FUNCTION tam.fn_add_command(
    p_id_device INT,
    p_command TEXT
)
RETURNS INT AS $$
DECLARE
    v_novo_id INT;
BEGIN
    INSERT INTO tam.commands (id_device, command_text)
    VALUES (p_id_device, p_command)
    RETURNING id INTO v_novo_id;

    RETURN v_novo_id;
END;
$$ LANGUAGE plpgsql;

-- Listar todos os comandos
CREATE OR REPLACE FUNCTION tam.fn_list_commands()
RETURNS SETOF tam.commands AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tam.commands ORDER BY id DESC;
END;
$$ LANGUAGE plpgsql;

-- comandos pendentes
CREATE OR REPLACE FUNCTION tam.fn_pending_commands(
    p_id_device INT
)
RETURNS SETOF tam.commands AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tam.commands
    WHERE id_device = p_id_device
      AND executed = FALSE
    ORDER BY id;
END;
$$ LANGUAGE plpgsql;