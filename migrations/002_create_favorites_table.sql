-- Migration: 002_create_favorites_table
-- Created at: 2026-10-09
-- Purpose: Create favorites table for student product wishlists

CREATE TABLE IF NOT EXISTS `favorites` (
    `favorite_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `added_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_favorite_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_favorite_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_favorite` (`user_id`, `product_id`)
);
