-- Migration: 003_seed_colleges_and_organizations
-- Created at: 2026-10-09
-- Purpose: Populate colleges and academic student organizations

INSERT IGNORE INTO `college` (`college_id`, `college_name`) VALUES
(1, 'College of Arts and Social Sciences'),
(2, 'College of Business Administration'),
(3, 'College of Computer Studies'),
(4, 'College of Education'),
(5, 'College of Engineering'),
(6, 'College of Health Sciences'),
(7, 'College of Science and Mathematics');

-- CSM Organizations
INSERT IGNORE INTO `organization` (`org_name`, `org_id`, `org_email`, `college_id`) VALUES
('CSM Chemistry Society', 'CHEMSOC', 'csm.chemsoc@g.msuiit.edu.ph', 7),
('CSM Haynayan Society', 'HAYNAYAN', 'csm.haynayan@g.msuiit.edu.ph', 7),
('CSM Kapisanan ng mga Mag-aaral sa Pisika', 'KMP', 'csm.kmp@g.msuiit.edu.ph', 7),
('CSM Marine Science Students Society', 'MASSTS', 'csm.massts@g.msuiit.edu.ph', 7),
('CSM Statistics and Mathematics Society', 'SMAS', 'csm.smas@g.msuiit.edu.ph', 7),
('CSM Biological Sciences Graduate Society', 'BSGS', 'csm.bsgs@g.msuiit.edu.ph', 7);

-- CED Organizations
INSERT IGNORE INTO `organization` (`org_name`, `org_id`, `org_email`, `college_id`) VALUES
('CED Association of Students Educators in Science and Math', 'ASSESMA', 'ced.assssma@g.msuiit.edu.ph', 4),
('CED Physical Education Student Organization', 'DPESO', 'ced.dpeso@g.msuiit.edu.ph', 4),
('CED SIDLAK', 'SIDLAK', 'ced.sidlak@g.msuiit.edu.ph', 4),
('CED Society of Language Educators', 'SLED', 'ced.sled@g.msuiit.edu.ph', 4),
('CED Student Tech and Entrep of the Philippines', 'STEP', 'ced.step@g.msuiit.edu.ph', 4);

-- COET Organizations
INSERT IGNORE INTO `organization` (`org_name`, `org_id`, `org_email`, `college_id`) VALUES
('COET Junior Philippine Institute of Civil Engineers', 'JPICE', 'coet.jpice@g.msuiit.edu.ph', 5),
('COET Association of Civil Engineering Students', 'ACES', 'coet.aces@g.msuiit.edu.ph', 5),
('COET Ceramics Engineering Society', 'CERES', 'coet.ceres@g.msuiit.edu.ph', 5),
('COET Electrical Engineering Technology Society', 'ELETS', 'coet.elets@g.msuiit.edu.ph', 5),
('COET Guild of Mining Engineering Students', 'GEMS', 'coet.gmes@g.msuiit.edu.ph', 5),
('COET Institute of Computer Engineering of the Phil SE', 'ICEPSE', 'coet.icepse@g.msuiit.edu.ph', 5),
('COET Institute of Integrated Electrical Engineering Students', 'IIEES', 'coet.iiees@g.msuiit.edu.ph', 5),
('COET Junior Institute of Elec and comm Engineering of the Phil', 'JIECEP', 'coet.jiecep@g.msuiit.edu.ph', 5),
('COET Junior Phillipines Institute of Chemical Engineers', 'JPICHE', 'coet.jpiche@g.msuiit.edu.ph', 5),
('COET Junior Phillipine Society of Mechanical Engineers', 'JPSME', 'coet.jpsm@g.msuiit.edu.ph', 5),
('COET Junior Society of Metallurgical Engineers of the Phil', 'JSMEP', 'coet.jsmep@g.msuiit.edu.ph', 5),
('COET Department of Chemical Engineering Technology', 'AGHIMUAN', 'coet.aghimuan@g.msuiit.edu.ph', 5),
('COET Junior Society Of Environmental Engineers of the Philippines', 'JSEEP', 'coet.jseep@g.msuiit.edu.ph', 5),
('COET Materials Engineering Technology Society', 'MaSETSo', 'masetso.mmt@gmail.com', 5),
('COET Junior Industrial Automation @ Mechatronics Society', 'JIAMS', 'societyofjiams@gmail.com', 5);

-- CASS Organizations
INSERT IGNORE INTO `organization` (`org_name`, `org_id`, `org_email`, `college_id`) VALUES
('Katastaasang Sanggunian ng mga Mag-aaral', 'KASAMA', 'kasama@g.msuiit.edu.ph', 1),
('CASS Historical society', 'HISTORYSOC', 'cass.histsoc@g.msuiit.edu.ph', 1),
('CASS Junior Philosophers Guild', 'JPG', 'cass.jpg@g.msuiit.edu.ph', 1),
('CASS Kabataang Pilipinong Aakay sa Bayan', 'KAPILAS BAYAN', 'cass.kapilasbayan@g.msuiit.edu.ph', 1),
('CASS Political Science Society', 'PSS', 'cass.pss@g.msuiit.edu.ph', 1),
('CASS Psychology Society', 'PSHCH-SOC', 'cass.psychsoc@g.msuiit.edu.ph', 1),
('CASS Sociology Society', 'SOCIO', 'cass.sociosoc@g.msuiit.edu.ph', 1),
('CASS Literature, Language, and Culture Society', 'LILACS', 'cass.abeo@g.msuiit.edu.ph', 1);

-- CEBA Organizations
INSERT IGNORE INTO `organization` (`org_name`, `org_id`, `org_email`, `college_id`) VALUES
('CEBA Junior Economics Society', 'JES', 'cbaa.jes@g.msuiit.edu.ph', 2),
('CEBA Junior Entrepreneurship and Marketing Society', 'JEMS', 'cbaa.jems@g.msuiit.edu.ph', 2),
('CEBA Society of Hospitality and Tourism Management', 'SHTM', 'cbaa.shtm@g.msuiit.edu.ph', 2),
('CEBA Junior Philippine Institute of Accountants', 'JPIA', 'cbaa.jpia@g.msuiit.edu.ph', 2);

-- CCS Organizations
INSERT IGNORE INTO `organization` (`org_name`, `org_id`, `org_email`, `college_id`) VALUES
('CCS Computer Application Officers', 'COM-APPS', 'ccs.cao@g.msuiit.edu.ph', 3),
('CCS Computer Science Society', 'COM-SOC', 'ccs.comsoc@g.msuiit.edu.ph', 3),
('CCS Junior Information Technology Society', 'JITS', 'ccs.jits@g.msuiit.edu.ph', 3);

-- Executive Councils
INSERT IGNORE INTO `organization` (`org_name`, `org_id`, `org_email`, `college_id`) VALUES
('CASS Executive Council', 'CASS-EC', 'cass.ec@g.msuiit.edu.ph', 1),
('CEBA Executive Council', 'CEBA-EC', 'cbaa.ec@g.msuiit.edu.ph', 2),
('CCS Executive Council', 'CCS-EC', 'ccs.ec@g.msuiit.edu.ph', 3),
('CED Executive Council', 'CED-EC', 'ced.ec@g.msuiit.edu.ph', 4),
('COET Executive Council', 'COET-EC', 'coet.ec@g.msuiit.edu.ph', 5),
('CON Executive Council', 'CON-EC', 'con.ec@g.msuiit.edu.ph', 6),
('CSM Executive Council', 'CSM-EC', 'csm.ec@g.msuiit.edu.ph', 7);
