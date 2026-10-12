CREATE DATABASE IF NOT EXISTS complaint_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE complaint_system;

CREATE TABLE users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 email VARCHAR(190) NOT NULL UNIQUE,
 phone VARCHAR(30),
 password_hash VARCHAR(255) NOT NULL,
 role ENUM('CITIZEN','AUTHORITY','ADMIN') NOT NULL DEFAULT 'CITIZEN',
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_users_role(role)
) ENGINE=InnoDB;

CREATE TABLE complaints (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 description TEXT NOT NULL,
 category VARCHAR(80) NOT NULL,
 priority ENUM('HIGH','MEDIUM','LOW') NOT NULL,
 ai_confidence DECIMAL(6,5) NOT NULL,
 latitude DECIMAL(10,7), longitude DECIMAL(10,7),
 address VARCHAR(500), image_path VARCHAR(500),
 status ENUM('PENDING','ASSIGNED','IN PROGRESS','RESOLVED','REJECTED') NOT NULL DEFAULT 'PENDING',
 assigned_to INT NULL,
 ai_signals JSON NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 INDEX idx_complaints_priority(priority), INDEX idx_complaints_status(status), INDEX idx_complaints_category(category), INDEX idx_complaints_created(created_at), INDEX idx_complaints_user(user_id),
 CONSTRAINT fk_complaints_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
 CONSTRAINT fk_complaints_assignee FOREIGN KEY(assigned_to) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE complaint_updates (
 id INT AUTO_INCREMENT PRIMARY KEY,
 complaint_id INT NOT NULL,
 updated_by INT NOT NULL,
 old_status VARCHAR(30), new_status VARCHAR(30) NOT NULL,
 note TEXT, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_updates_complaint(complaint_id),
 CONSTRAINT fk_updates_complaint FOREIGN KEY(complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
 CONSTRAINT fk_updates_user FOREIGN KEY(updated_by) REFERENCES users(id)
) ENGINE=InnoDB;
