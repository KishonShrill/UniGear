-- Migration: 004_seed_sizes_and_users
-- Created at: 2026-10-09
-- Purpose: Seed standard clothing sizes and initial student / seller accounts

INSERT IGNORE INTO `sizes` (`size_id`, `size_name`) VALUES
(1, 'XS'),
(2, 'S'),
(3, 'M'),
(4, 'L'),
(5, 'XL'),
(6, '2XL');

INSERT IGNORE INTO `user` (`user_id`, `user_name`, `user_email`, `user_password`, `user_contact`, `user_address`, `user_role`, `org_id`) VALUES
(1, 'Alice Thompson', 'alice.thompson@example.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '09876543210', '456 Forest St, Iligan City', 'user', 'CASS-EC'),
(2, 'Brian Lee', 'brian.lee@example.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '08765432109', '789 Hill St, Iligan City', 'user', 'CEBA-EC'),
(3, 'Catherine Kim', 'catherine.kim@example.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '07654321098', '321 River St, Iligan City', 'user', 'CCS-EC'),
(4, 'David Yang', 'david.yang@example.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '06543210987', '654 Lake St, Iligan City', 'user', 'CED-EC'),
(5, 'Ella Chen', 'ella.chen@example.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '05432109876', '987 Ocean St, Iligan City', 'user', 'COET-EC'),
(6, 'Frank Martinez', 'frank.martinez@example.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '04321098765', '135 Mountain St, Iligan City', 'user', 'CON-EC'),
(7, 'Grace Wong', 'grace.wong@example.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '03210987654', '246 Valley St, Iligan City', 'user', 'CON-EC'),
(8, 'Unigear Admin', 'unigear@gmail.com', 'scrypt:32768:8:1$7G5Ws6expNwz74Nk$e73858dc060d0d43fd22a3ae6e2a65dafbedbad6b30c5bde59652a4e98631826fdfa89d7bdc30f94fc4f99df85d74bafeacb7eec5a1bb2805afbcbc554131dac', '02109876543', '357 Meadow St, Iligan City', 'seller', 'CCS-EC'),
(9, 'Emmanuel Fitz Ciano', 'emmanuelfitz.ciano@g.msuiit.edu.ph', NULL, NULL, NULL, 'seller', 'CASS-EC'),
(10, 'Hussam Bansao', 'hussam.bansao@g.msuiit.edu.ph', NULL, NULL, NULL, 'seller', 'CEBA-EC'),
(11, 'Lavigne Sistona', 'lavignekaye.sistona@g.msuiit.edu.ph', NULL, NULL, NULL, 'seller', 'CASS-EC'),
(12, 'Chriscent Pingol', 'chriscentlouisjune.pingol@g.msuiit.edu.ph', NULL, NULL, NULL, 'seller', 'CCS-EC');
