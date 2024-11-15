DROP DATABASE if EXISTS `college_marketplace`;
CREATE DATABASE if NOT EXISTS `college_marketplace`;
USE `college_marketplace`;


DROP TABLE if EXISTS `college`;
CREATE TABLE if NOT EXISTS `college` (
	college_id INT AUTO_INCREMENT PRIMARY KEY,
	college_name VARCHAR(255) NOT NULL,
	UNIQUE KEY unique_college_name (college_name)
);


DROP TABLE if EXISTS `organization`;
CREATE TABLE if NOT EXISTS `organization` (
	org_id VARCHAR(30) PRIMARY KEY,
	org_name VARCHAR(255) NOT NULL,
	org_email VARCHAR(199),
	college_id INT NOT NULL,
	UNIQUE KEY unique_org_name (org_name),
	CONSTRAINT `fk_org_college` FOREIGN KEY (college_id) REFERENCES `college` (college_id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);


DROP TABLE if EXISTS `user`;
CREATE TABLE if NOT EXISTS `user` (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
	user_name VARCHAR(30) NOT NULL,
	user_email VARCHAR(99) NOT NULL,
	user_password VARCHAR(199) DEFAULT NULL,
	user_contact CHAR(11) DEFAULT NULL,
	user_address VARCHAR(199) DEFAULT NULL,
	user_role VARCHAR(6) DEFAULT NULL,
	org_id VARCHAR(30) DEFAULT NULL,
	UNIQUE KEY username_exists (user_name),
	UNIQUE KEY email_exists (user_email),
	UNIQUE KEY number_exists (user_contact),
	CONSTRAINT `fk_user_org` FOREIGN KEY (org_id) REFERENCES `organization` (org_id) ON UPDATE CASCADE ON DELETE CASCADE
);


DROP TABLE if EXISTS `sizes`;
CREATE TABLE if NOT EXISTS `sizes` (
	size_id INT AUTO_INCREMENT PRIMARY KEY,
	size_name VARCHAR(10) NOT NULL
);


DROP TABLE if EXISTS `products`;
CREATE TABLE if NOT EXISTS `products` (
	product_id INT AUTO_INCREMENT PRIMARY KEY,
	product_name VARCHAR(199) NOT NULL,
	description TEXT NOT NULL,
	hook VARCHAR(99) DEFAULT NULL,
	type VARCHAR(30) NOT NULL,
	price DECIMAL(10, 2),
	order_type BOOLEAN,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`seller_id` INT,
	CONSTRAINT `fk_product_user` FOREIGN KEY (seller_id) REFERENCES `user` (user_id)
);


DROP TABLE if EXISTS `product_sizes`;
CREATE TABLE if NOT EXISTS `product_sizes` (
	product_id INT,
	product_quantity INT,
	size_id INT,
   FOREIGN KEY (product_id) REFERENCES products (product_id),
   FOREIGN KEY (size_id) REFERENCES sizes (size_id)
);


DROP TABLE if EXISTS `pictures`;
CREATE TABLE if NOT EXISTS `pictures` (
	picture_id INT,
	picture_url TEXT,
	CONSTRAINT `fk_picture_product` FOREIGN KEY (picture_id) REFERENCES `products` (product_id)
);


DROP TABLE if EXISTS `ordered_by`;
CREATE TABLE if NOT EXISTS `ordered_by` (
	order_id INT AUTO_INCREMENT PRIMARY KEY,
	user_id INT NOT NULL,
	product_id INT NOT NULL,
	size_id INT NOT NULL,
	quantity INT NOT NULL,
	total_cost DECIMAL(10, 2) NOT NULL,
	order_status BOOLEAN NOT NULL,
	purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT `fk_order_user` FOREIGN KEY (user_id) REFERENCES `user` (user_id),
	CONSTRAINT `fk_order_product` FOREIGN KEY (product_id) REFERENCES `products` (product_id),
	CONSTRAINT `fk_order_size` FOREIGN KEY (size_id) REFERENCES `sizes` (size_id)
);


-- Below is the sample data
-- Below is the sample data
-- Below is the sample data
INSERT INTO college (college_name) VALUES 
('College of Engineering'), 
('College of Arts and Sciences'), 
('College of Business Administration'), 
('College of Education');

INSERT INTO organization (org_id, org_name, college_id, org_email) VALUES 
('KASAMA', 'Kataastaasang Sanggunian ng mga Mag-aaral', 1, "kasama@g.msuiit.edu.ph"), 
('AS', 'Art Society', 2, NULL), 
('BO', 'Business Organization', 3, NULL), 
('FE', 'Future Educators', 4, NULL);

INSERT INTO user (user_name, user_email, user_password, user_contact, user_address, user_role, org_id) VALUES 
('Alice Thompson', 'alice.thompson@example.com', 'securepassword1', '9876543210', '456 Forest St, Iligan City', 'user', 'KASAMA'), 
('Brian Lee', 'brian.lee@example.com', 'securepassword2', '8765432109', '789 Hill St, Iligan City', 'user', 'AS'), 
('Catherine Kim', 'catherine.kim@example.com', 'securepassword3', '7654321098', '321 River St, Iligan City', 'seller', 'KASAMA'), 
('David Yang', 'david.yang@example.com', 'securepassword4', '6543210987', '654 Lake St, Iligan City', 'user', 'BO'), 
('Ella Chen', 'ella.chen@example.com', 'securepassword5', '5432109876', '987 Ocean St, Iligan City', 'seller', 'AS'), 
('Frank Martinez', 'frank.martinez@example.com', 'securepassword6', '4321098765', '135 Mountain St, Iligan City', 'user', 'KASAMA'), 
('Grace Wong', 'grace.wong@example.com', 'securepassword7', '3210987654', '246 Valley St, Iligan City', 'user', 'FE'), 
('Henry Johnson', 'henry.johnson@example.com', 'securepassword8', '2109876543', '357 Meadow St, Iligan City', 'seller', 'BO');

INSERT INTO sizes (size_name) VALUES 
('XS'),
('S'), 
('M'), 
('L'), 
('XL'), 
('2XL');

INSERT INTO products (product_name, description, hook, type, price, seller_id, order_type) VALUES 
('Basic T-Shirt', 'A simple and comfortable t-shirt.', 'Great for everyday wear', 'Clothing', 15.99, 1, 1),
('Hoodie', 'A warm and stylish hoodie for cool weather.', 'Stay cozy and fashionable', 'Clothing', 29.99, 2, 0),
('Running Shoes', 'Lightweight shoes for all your running needs.', 'Perfect for athletes', 'Footwear', 49.99, 3, 1),
('Jeans', 'Classic fit jeans that never go out of style.', 'Dress them up or down', 'Clothing', 39.99, 4, 0);

INSERT INTO product_sizes (product_id, product_quantity, size_id) VALUES 
(1, 50, 1),  -- Basic T-Shirt, 50 quantity in Size S
(1, 30, 2),  -- Basic T-Shirt, 30 quantity in Size M
(1, 20, 3),  -- Basic T-Shirt, 20 quantity in Size L
(2, 15, 1),  -- Hoodie, 15 quantity in Size S
(2, 25, 2),  -- Hoodie, 25 quantity in Size M
(2, 10, 3),  -- Hoodie, 10 quantity in Size L
(3, 40, 1),  -- Running Shoes, 40 quantity in Size S
(3, 30, 2),  -- Running Shoes, 30 quantity in Size M
(4, 20, 1),  -- Jeans, 20 quantity in Size S
(4, 15, 2),  -- Jeans, 15 quantity in Size M
(4, 10, 3);  -- Jeans, 10 quantity in Size L

INSERT INTO ordered_by (user_id, product_id, size_id, quantity, total_cost, order_status) VALUES 
(1, 1, 1, 1, 15.99, true),  -- John Doe orders 2 Engineering T-Shirts
(1, 3, 3, 1, 15.99, false),  -- John Doe orders 1 Business Planner
(3, 2, 2, 1, 15.99, false),  -- Mark Johnson orders 3 Art Supplies Kits
(4, 4, 4, 1, 15.99, true);  -- Emily Davis orders 1 Teacher's Guide