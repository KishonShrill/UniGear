-- Migration: 005_seed_sample_products
-- Created at: 2026-10-09
-- Purpose: Seed sample merchandise products, size variations, and picture URLs

INSERT IGNORE INTO `products` (`product_id`, `product_name`, `description`, `hook`, `type`, `price`, `order_type`, `seller_id`, `release_date`, `preorder_goal`) VALUES
(1, 'Hoodie', 'Stay cozy and stylish with our premium hoodie, crafted from soft, breathable fabric to keep you comfortable all day long. Featuring a spacious front pocket, an adjustable drawstring hood, and a relaxed fit, this hoodie is perfect for layering or lounging. Whether you are heading out or staying in, it is the ultimate combination of comfort and style.', NULL, 'hoodie', 450.00, 0, 12, NULL, 30),
(2, 'Software Freedom Day (BLACK)', 'Celebrate open-source innovation with our Software Freedom Day Black Hoodie! Made from premium, soft cotton blend fabric, this hoodie offers unmatched comfort and durability. Featuring a minimalist design with the iconic Software Freedom Day logo, it is perfect for showcasing your passion for software freedom and community-driven technology. With a cozy front pocket and adjustable drawstring hood, this sleek black hoodie combines functionality with a statement. Ideal for tech enthusiasts and open-source advocates alike!', NULL, 't-shirt', 300.00, 0, 12, NULL, 30),
(3, 'Software Freedom Day (WHITE)', 'Celebrate open-source innovation with our Software Freedom Day White Hoodie! Made from premium, soft cotton blend fabric, this hoodie offers unmatched comfort and durability. Featuring a minimalist design with the iconic Software Freedom Day logo, it is perfect for showcasing your passion for software freedom and community-driven technology. With a cozy front pocket and adjustable drawstring hood, this sleek white hoodie combines functionality with a statement. Ideal for tech enthusiasts and open-source advocates alike!', NULL, 't-shirt', 300.00, 0, 12, NULL, 30),
(4, 'the pack (white)', 'Unleash your inner strength with The Pack White Hoodie, inspired by the spirit of wolves. Crafted from high-quality fabric, this hoodie offers a perfect blend of comfort and durability for everyday wear. Featuring a bold wolf-themed design, it embodies unity, resilience, and power. At just 530 pesos, it is an affordable yet stylish way to stay cozy and make a statement. Complete with a spacious front pocket and adjustable hood, this hoodie is perfect for those who run with the pack.', NULL, 't-shirt', 530.00, 0, 12, NULL, 30),
(5, 'The pack (black)', 'Unleash your inner strength with The Pack Black Hoodie, inspired by the spirit of wolves. Crafted from high-quality fabric, this hoodie offers a perfect blend of comfort and durability for everyday wear. Featuring a bold wolf-themed design, it embodies unity, resilience, and power. At just 530 pesos, it is an affordable yet stylish way to stay cozy and make a statement. Complete with a spacious front pocket and adjustable hood, this hoodie is perfect for those who run with the pack.', NULL, 't-shirt', 530.00, 0, 12, NULL, 30),
(6, 'Golden Griffins', 'Show off your legendary style with the Golden Griffins Bundle! For only 1,000 pesos, this exclusive set includes: A pair of sleek black and white t-shirts, perfect for everyday wear, A bold yellow shirt with a unique design to stand out in any crowd, A stylish lanyard to keep your essentials close, A durable tote bag, perfect for carrying all your essentials in griffin-worthy fashion. This bundle combines practicality and flair, making it the ultimate collection for fans of the Golden Griffins.', NULL, 't-shirt', 1000.00, 0, 8, NULL, 30);

INSERT IGNORE INTO `product_sizes` (`product_id`, `product_quantity`, `size_id`) VALUES
(1, 0, 2),
(1, 0, 3),
(1, 0, 4),
(2, 0, 2),
(2, 0, 3),
(2, 0, 4),
(3, 0, 2),
(3, 0, 3),
(3, 0, 4),
(4, 0, 2),
(4, 0, 3),
(4, 0, 4),
(5, 0, 2),
(5, 0, 3),
(5, 0, 4),
(6, 0, 1),
(6, 0, 2),
(6, 0, 3),
(6, 0, 4),
(6, 0, 5),
(6, 0, 6);

INSERT IGNORE INTO `pictures` (`picture_id`, `picture_url`) VALUES
(1, 'https://res.cloudinary.com/dlmabgte3/image/upload/v1734621715/Hoodie.png'),
(2, 'https://res.cloudinary.com/dlmabgte3/image/upload/v1734517452/458367390_529211662799380_1443592312072245402_n.jpg.jpg'),
(3, 'https://res.cloudinary.com/dlmabgte3/image/upload/v1734517329/458482486_529211629466050_4673141915609240596_n.jpg.jpg'),
(4, 'https://res.cloudinary.com/dlmabgte3/image/upload/v1734517995/439741217_836588071837001_5274681254830574886_n.jpg.jpg'),
(5, 'https://res.cloudinary.com/dlmabgte3/image/upload/v1734517939/439888544_836588051837003_1021380121025332956_n.jpg.jpg'),
(6, 'https://res.cloudinary.com/dlmabgte3/image/upload/v1734576381/461784716_1076625114473068_3761187242483832277_n.jpg.jpg');
