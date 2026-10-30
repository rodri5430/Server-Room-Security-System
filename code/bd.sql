Código para criação das tabelas

1 - Utilizadores ("users")
CREATE TABLE tam.users (
    id SERIAL PRIMARY KEY,
    nif INT(9) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
)

2 - Valor Sensor Temperatura (temp_readings)
CREATE TABLE tam.temp_readings(
    id SERIAL PRIMARY KEY,
    id_device INT REFERENCES devices(id) ON DELETE CASCADE,
    temperature_value NUMERIC(5,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

3 - Dados de Acesso (access_logs) 
CREATE TABLE tam.access_logs (
    id SERIAL PRIMARY KEY,
    id_user INT REFERENCES users(id) ON DELETE CASCADE,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login_exit_time TIMESTAMP DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'success' -- ex: success, failed
);

4 - Comandos (commands)
CREATE TABLE tam.commands (
    id SERIAL PRIMARY KEY,
    id_user INT REFERENCES users(id) ON DELETE SET NULL,
    command_text TEXT NOT NULL
);

5 - Eventos de Alarme (alarm_events)
    
    CREATE TABLE tam.alarm_events (
        id SERIAL PRIMARY KEY,
        id_device INT REFERENCES TAM.device(id) ON DELETE CASCADE,
        trigger_reason VARCHAR(100) NOT NULL, -- ex: 'HIGH_TEMPERATURE', 'MANUAL_ACTIVATION'
        triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP DEFAULT NULL
    );

6 - Dispositivos (devices) (Vai estar associado a tabela de alarmes)    

CREATE TABLE tam.device(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model VARCHAR(50),
    id_alarme_events INT REFERENCES alarm_events(id) ON DELETE SET NULL
);
