CREATE DATABASE IF NOT EXISTS penademorte
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE penademorte;

CREATE TABLE IF NOT EXISTS admins (
    id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    reset_token VARCHAR(255) NULL,
    reset_token_expires_at DATETIME NULL,
    CONSTRAINT pk_admins PRIMARY KEY (id),
    CONSTRAINT uk_admins_email UNIQUE (email),
    INDEX idx_admins_reset_token (reset_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT uk_users_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS questions (
    id INT NOT NULL AUTO_INCREMENT,
    text TEXT NOT NULL,
    content JSON NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    order_index INT NOT NULL DEFAULT 0,
    CONSTRAINT pk_questions PRIMARY KEY (id),
    INDEX idx_questions_active_order (active, order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS answers (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_value ENUM('yes', 'no') NOT NULL,
    CONSTRAINT pk_answers PRIMARY KEY (id),
    CONSTRAINT uk_answers_user_question UNIQUE (user_id, question_id),
    CONSTRAINT fk_answers_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_answers_question
        FOREIGN KEY (question_id) REFERENCES questions (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_answers_question_value (question_id, answer_value),
    INDEX idx_answers_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ads (
    id INT NOT NULL AUTO_INCREMENT,
    tipo ENUM('image', 'youtube', 'video') NOT NULL,
    url VARCHAR(500) NOT NULL,
    link VARCHAR(500) NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id INT NOT NULL,
    question_id INT NOT NULL,
    CONSTRAINT pk_ads PRIMARY KEY (id),
    CONSTRAINT fk_ads_created_by
        FOREIGN KEY (created_by_id) REFERENCES admins (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_ads_question
        FOREIGN KEY (question_id) REFERENCES questions (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    INDEX idx_ads_tipo (tipo),
    INDEX idx_ads_created_by_id (created_by_id),
    INDEX idx_ads_question_ativo (question_id, ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
