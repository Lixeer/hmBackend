-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS hospital DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hospital;

-- 1. patient 表
CREATE TABLE IF NOT EXISTS patient (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    age INT NOT NULL COMMENT '年龄',
    gender VARCHAR(10) NOT NULL COMMENT '性别',
    room_number VARCHAR(20) NOT NULL COMMENT '病房号',
    status VARCHAR(20) DEFAULT 'normal' COMMENT '状态：normal-正常，warning-警告，critical-危急',
    severity INT DEFAULT 0 COMMENT '异常等级，0正常，1-5数值越大越严重',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_room_number (room_number),
    INDEX idx_status (status),
    INDEX idx_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='患者信息表';

-- 2. behavior_log 表
CREATE TABLE IF NOT EXISTS behavior_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL COMMENT '患者ID',
    behavior_type VARCHAR(50) NOT NULL COMMENT '行为类型',
    description VARCHAR(255) COMMENT '行为描述',
    is_abnormal TINYINT DEFAULT 0 COMMENT '是否异常：0-正常，1-异常',
    record_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    INDEX idx_patient_id (patient_id),
    INDEX idx_behavior_type (behavior_type),
    INDEX idx_is_abnormal (is_abnormal),
    INDEX idx_record_time (record_time),
    FOREIGN KEY (patient_id) REFERENCES patient(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行为日志表';
