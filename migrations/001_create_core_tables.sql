-- Migration: 001_create_core_tables
-- Created at: 2026-10-09
-- Purpose: Initial core schema tables for UniGear College Marketplace

CREATE TABLE IF NOT EXISTS `college` (
    `college_id` INT AUTO_INCREMENT PRIMARY KEY,
    `college_name` VARCHAR(255) NOT NULL,
    UNIQUE KEY `unique_college_name` (`college_name`)
);

CREATE TABLE IF NOT EXISTS `organization` (
    `org_id` VARCHAR(30) PRIMARY KEY,
    `org_name` VARCHAR(255) NOT NULL,
    `org_email` VARCHAR(199) DEFAULT NULL,
    `college_id` INT NOT NULL,
    UNIQUE KEY `unique_org_name` (`org_name`),
    CONSTRAINT `fk_org_college` FOREIGN KEY (`college_id`) REFERENCES `college` (`college_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `user` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_name` VARCHAR(199) NOT NULL,
    `user_email` VARCHAR(99) NOT NULL,
    `user_password` VARCHAR(199) DEFAULT NULL,
    `user_contact` CHAR(11) DEFAULT NULL,
    `user_address` VARCHAR(199) DEFAULT NULL,
    `user_role` VARCHAR(6) DEFAULT NULL,
    `org_id` VARCHAR(30) DEFAULT NULL,
    UNIQUE KEY `username_exists` (`user_name`),
    UNIQUE KEY `email_exists` (`user_email`),
    UNIQUE KEY `number_exists` (`user_contact`),
    CONSTRAINT `fk_user_org` FOREIGN KEY (`org_id`) REFERENCES `organization` (`org_id`) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `sizes` (
    `size_id` INT AUTO_INCREMENT PRIMARY KEY,
    `size_name` VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS `products` (
    `product_id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_name` VARCHAR(199) NOT NULL,
    `description` TEXT NOT NULL,
    `hook` VARCHAR(99) DEFAULT NULL,
    `type` VARCHAR(30) NOT NULL,
    `price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `order_type` BOOLEAN DEFAULT 0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `seller_id` INT DEFAULT NULL,
    `release_date` DATE DEFAULT NULL,
    `preorder_goal` INT DEFAULT NULL,
    CONSTRAINT `fk_product_user` FOREIGN KEY (`seller_id`) REFERENCES `user` (`user_id`) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS `product_sizes` (
    `product_id` INT NOT NULL,
    `product_quantity` INT NOT NULL DEFAULT 0,
    `size_id` INT NOT NULL,
    CONSTRAINT `fk_ps_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_ps_size` FOREIGN KEY (`size_id`) REFERENCES `sizes` (`size_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `pictures` (
    `picture_id` INT NOT NULL,
    `picture_url` TEXT NOT NULL,
    CONSTRAINT `fk_picture_product` FOREIGN KEY (`picture_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `ordered_by` (
    `order_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `size_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `total_cost` DECIMAL(10, 2) NOT NULL,
    `order_status` BOOLEAN NOT NULL DEFAULT 0,
    `order_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `proof_of_payment` VARCHAR(255) DEFAULT NULL,
    CONSTRAINT `fk_order_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_order_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_order_size` FOREIGN KEY (`size_id`) REFERENCES `sizes` (`size_id`)
);
