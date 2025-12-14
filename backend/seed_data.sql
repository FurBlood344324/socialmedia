-- ============================================
-- INITIAL SEED DATA
-- ============================================

INSERT INTO Roles (role_name) VALUES ('admin'), ('moderator'), ('member') ON CONFLICT DO NOTHING;
INSERT INTO PrivacyTypes (privacy_name) VALUES ('public'), ('private') ON CONFLICT DO NOTHING;
INSERT INTO FollowStatus (status_name) VALUES ('pending'), ('accepted'), ('rejected') ON CONFLICT DO NOTHING;

-- ============================================
-- 1. USERS
-- ============================================

INSERT INTO Users (username, email, password_hash, bio, is_private, profile_picture_url) VALUES
('admin_user', 'admin@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'System Administrator', FALSE, 'http://localhost:5000/static/uploads/admin_user_1765732581_default.png'),
('john_doe', 'john@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Just a regular guy loving SQL', FALSE, 'http://localhost:5000/static/uploads/john_doe_1765732582_default.png'),
('jane_smith', 'jane@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Photography and Travel', TRUE, 'http://localhost:5000/static/uploads/jane_smith_1765732582_default.png'),
('mehmet_yilmaz', 'mehmet@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Yazılım ve Teknoloji', FALSE, 'http://localhost:5000/static/uploads/mehmet_yilmaz_1765732582_default.png'),
('ayse_demir', 'ayse@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Gezgin, Yemek Tutkunu, Doğa Sever', FALSE, 'http://localhost:5000/static/uploads/ayse_demir_1765732582_default.png'),
('baris_ozcan', 'baris@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Sanat, Tasarım ve Teknoloji', FALSE, 'http://localhost:5000/static/uploads/baris_ozcan_1765732583_default.png'),
('zeynep_kaya', 'zeynep@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Kitaplar ve Kahve', FALSE, 'http://localhost:5000/static/uploads/zeynep_kaya_1765732583_default.png'),
('ali_yildiz', 'ali@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Spor, Futbol, Fitness', FALSE, 'http://localhost:5000/static/uploads/ali_yildiz_1765732583_default.png'),
('selin_karaca', 'selin@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Moda ve Güzellik', FALSE, 'http://localhost:5000/static/uploads/selin_karaca_1765732583_default.png'),
('can_turan', 'can@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Oyunlar, E-spor, Yayıncılık', FALSE, 'http://localhost:5000/static/uploads/can_turan_1765732584_default.png'),
('elif_su', 'elif@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Mimarlık ve Tasarım', TRUE, 'http://localhost:5000/static/uploads/elif_su_1765732584_default.png'),
('burak_celik', 'burak@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Motosiklet Tutkunu', FALSE, 'http://localhost:5000/static/uploads/burak_celik_1765732584_default.png'),
('deniz_mavi', 'deniz@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Dalış ve Su Sporları', FALSE, 'http://localhost:5000/static/uploads/deniz_mavi_1765732584_default.png'),
('gizem_ay', 'gizem@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Astroloji ve Meditasyon', FALSE, 'http://localhost:5000/static/uploads/gizem_ay_1765732585_default.png'),
('ozgur_ruh', 'ozgur@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Kamp ve Doğa', FALSE, 'http://localhost:5000/static/uploads/ozgur_ruh_1765732585_default.png'),
('teknoloji_kurtu', 'tekno@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Yeni Çıkan Gadgetlar', FALSE, 'http://localhost:5000/static/uploads/teknoloji_kurtu_1765732585_default.png'),
('sinema_elestirmeni', 'sinema@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Film İncelemeleri', FALSE, 'http://localhost:5000/static/uploads/sinema_elestirmeni_1765732585_default.png'),
('muzik_ruhu', 'muzik@example.com', 'scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263', 'Gitar ve Piyano', FALSE, 'http://localhost:5000/static/uploads/muzik_ruhu_1765732586_default.png')
ON CONFLICT DO NOTHING;

-- ============================================
-- 2. COMMUNITIES
-- ============================================

INSERT INTO Communities (name, description, creator_id, privacy_id) VALUES
('Python Lovers', 'A community for Python enthusiasts', (SELECT user_id FROM Users WHERE username='admin_user'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public')),
('Travel Diaries', 'Share your travel stories', (SELECT user_id FROM Users WHERE username='jane_smith'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public')),
('Secret Society', 'Invite only', (SELECT user_id FROM Users WHERE username='john_doe'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='private')),
('Lezzetli Tarifler', 'En güzel yemek tarifleri burada', (SELECT user_id FROM Users WHERE username='ayse_demir'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public')),
('Teknoloji Dünyası', 'Son teknoloji haberleri ve tartışmalar', (SELECT user_id FROM Users WHERE username='mehmet_yilmaz'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public')),
('Sinema Kulübü', 'Film ve dizi önerileri', (SELECT user_id FROM Users WHERE username='sinema_elestirmeni'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public')),
('Oyun Evreni', 'PC, Konsol ve Mobil Oyunlar', (SELECT user_id FROM Users WHERE username='can_turan'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public')),
('Doğa Fotoğrafçıları', 'Doğadan en güzel kareler', (SELECT user_id FROM Users WHERE username='jane_smith'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public')),
('Kitap Kurdu', 'Okuduğunuz kitapları paylaşın', (SELECT user_id FROM Users WHERE username='zeynep_kaya'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='public'))
ON CONFLICT DO NOTHING;

-- ============================================
-- 3. COMMUNITY MEMBERS
-- ============================================

INSERT INTO CommunityMembers (community_id, user_id, role_id) VALUES
-- Python Lovers
((SELECT community_id FROM Communities WHERE name='Python Lovers'), (SELECT user_id FROM Users WHERE username='john_doe'), (SELECT role_id FROM Roles WHERE role_name='member')),
((SELECT community_id FROM Communities WHERE name='Python Lovers'), (SELECT user_id FROM Users WHERE username='mehmet_yilmaz'), (SELECT role_id FROM Roles WHERE role_name='moderator')),
((SELECT community_id FROM Communities WHERE name='Python Lovers'), (SELECT user_id FROM Users WHERE username='teknoloji_kurtu'), (SELECT role_id FROM Roles WHERE role_name='member')),

-- Lezzetli Tarifler
((SELECT community_id FROM Communities WHERE name='Lezzetli Tarifler'), (SELECT user_id FROM Users WHERE username='gizem_ay'), (SELECT role_id FROM Roles WHERE role_name='member')),
((SELECT community_id FROM Communities WHERE name='Lezzetli Tarifler'), (SELECT user_id FROM Users WHERE username='selin_karaca'), (SELECT role_id FROM Roles WHERE role_name='member')),

-- Teknoloji Dünyası
((SELECT community_id FROM Communities WHERE name='Teknoloji Dünyası'), (SELECT user_id FROM Users WHERE username='can_turan'), (SELECT role_id FROM Roles WHERE role_name='moderator')),
((SELECT community_id FROM Communities WHERE name='Teknoloji Dünyası'), (SELECT user_id FROM Users WHERE username='ali_yildiz'), (SELECT role_id FROM Roles WHERE role_name='member')),

-- Sinema Kulübü
((SELECT community_id FROM Communities WHERE name='Sinema Kulübü'), (SELECT user_id FROM Users WHERE username='baris_ozcan'), (SELECT role_id FROM Roles WHERE role_name='member')),

-- Oyun Evreni
((SELECT community_id FROM Communities WHERE name='Oyun Evreni'), (SELECT user_id FROM Users WHERE username='burak_celik'), (SELECT role_id FROM Roles WHERE role_name='member'))
ON CONFLICT DO NOTHING;

-- ============================================
-- 4. FOLLOWS
-- ============================================

INSERT INTO Follows (follower_id, following_id, status_id) VALUES
-- John follows Jane
((SELECT user_id FROM Users WHERE username='john_doe'), (SELECT user_id FROM Users WHERE username='jane_smith'), (SELECT status_id FROM FollowStatus WHERE status_name='pending')),
-- Jane follows John (Accepted)
((SELECT user_id FROM Users WHERE username='jane_smith'), (SELECT user_id FROM Users WHERE username='john_doe'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),

-- Mehmet follows Tech people
((SELECT user_id FROM Users WHERE username='mehmet_yilmaz'), (SELECT user_id FROM Users WHERE username='teknoloji_kurtu'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),
((SELECT user_id FROM Users WHERE username='mehmet_yilmaz'), (SELECT user_id FROM Users WHERE username='can_turan'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),

-- Ayse follows lifestyle people
((SELECT user_id FROM Users WHERE username='ayse_demir'), (SELECT user_id FROM Users WHERE username='gizem_ay'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),
((SELECT user_id FROM Users WHERE username='ayse_demir'), (SELECT user_id FROM Users WHERE username='selin_karaca'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),

-- Create a small dense network for Friend of Friend
((SELECT user_id FROM Users WHERE username='ali_yildiz'), (SELECT user_id FROM Users WHERE username='burak_celik'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),
((SELECT user_id FROM Users WHERE username='burak_celik'), (SELECT user_id FROM Users WHERE username='can_turan'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),
((SELECT user_id FROM Users WHERE username='can_turan'), (SELECT user_id FROM Users WHERE username='deniz_mavi'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')),
((SELECT user_id FROM Users WHERE username='deniz_mavi'), (SELECT user_id FROM Users WHERE username='ali_yildiz'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted'))
ON CONFLICT DO NOTHING;

-- ============================================
-- 5. POSTS
-- ============================================

INSERT INTO Posts (user_id, community_id, content) VALUES
-- Basic posts
((SELECT user_id FROM Users WHERE username='john_doe'), (SELECT community_id FROM Communities WHERE name='Python Lovers'), 'Just started learning Python, it is amazing! #python #learning'),
((SELECT user_id FROM Users WHERE username='jane_smith'), (SELECT community_id FROM Communities WHERE name='Travel Diaries'), 'Visiting Istanbul this summer! The Bosphorus is beautiful. #istanbul #travel'),
((SELECT user_id FROM Users WHERE username='mehmet_yilmaz'), NULL, 'Veritabanı optimizasyonu hakkında ipuçları. Index kullanımı çok önemli. #sql #database'),

-- Ayse posts
((SELECT user_id FROM Users WHERE username='ayse_demir'), (SELECT community_id FROM Communities WHERE name='Lezzetli Tarifler'), 'Bugün harika bir karnıyarık yaptım! İşte tarifi... #yemek #tarif'),
((SELECT user_id FROM Users WHERE username='ayse_demir'), NULL, 'Hafta sonu Kapadokya gezisi planlıyoruz. Önerisi olan var mı? #gezi #kapadokya'),

-- Teknoloji posts
((SELECT user_id FROM Users WHERE username='mehmet_yilmaz'), (SELECT community_id FROM Communities WHERE name='Teknoloji Dünyası'), 'Yapay zeka modelleri giderek gelişiyor. Gelecek heyecan verici! #ai #tech'),
((SELECT user_id FROM Users WHERE username='teknoloji_kurtu'), (SELECT community_id FROM Communities WHERE name='Teknoloji Dünyası'), 'Yeni çıkan ekran kartlarını incelediniz mi? Fiyatlar uçmuş durumda. #gpu #hardware'),

-- Sinema posts
((SELECT user_id FROM Users WHERE username='sinema_elestirmeni'), (SELECT community_id FROM Communities WHERE name='Sinema Kulübü'), 'Christopher Nolan filmleri her zaman düşündürücü oluyor. Siz ne düşünüyorsunuz? #sinema #nolan'),
((SELECT user_id FROM Users WHERE username='baris_ozcan'), (SELECT community_id FROM Communities WHERE name='Sinema Kulübü'), 'Bilim kurgu filmleri arasında en sevdiğim Interstellar. Müzikleri efsane. #hanszimmer'),

-- Oyun posts
((SELECT user_id FROM Users WHERE username='can_turan'), (SELECT community_id FROM Communities WHERE name='Oyun Evreni'), 'League of Legends dünya şampiyonası başlıyor! Favoriniz kim? #lol #esport'),
((SELECT user_id FROM Users WHERE username='burak_celik'), (SELECT community_id FROM Communities WHERE name='Oyun Evreni'), 'Elden Ring oynamaya yeni başladım. Çok zor ama keyifli. #darksouls #eldenring'),

-- Doğa posts
((SELECT user_id FROM Users WHERE username='deniz_mavi'), (SELECT community_id FROM Communities WHERE name='Doğa Fotoğrafçıları'), 'Bugün su altında çektiğim kaplumbağa fotoğrafı. #diving #nature'),
((SELECT user_id FROM Users WHERE username='ozgur_ruh'), (SELECT community_id FROM Communities WHERE name='Doğa Fotoğrafçıları'), 'Kamp ateşinin başında huzur... #camping #peace'),

-- General user posts
((SELECT user_id FROM Users WHERE username='zeynep_kaya'), (SELECT community_id FROM Communities WHERE name='Kitap Kurdu'), 'Dostoyevski okumaya Suç ve Ceza ile başlamalı mıyım? #kitap #edebiyat'),
((SELECT user_id FROM Users WHERE username='ali_yildiz'), NULL, 'Bugünkü antrenman çok yorucuydu ama değdi. Asla pes etme! #fitness #motivation'),
((SELECT user_id FROM Users WHERE username='selin_karaca'), NULL, 'Bu senenin renkleri çok canlı! Neon renkler geri dönüyor. #fashion #trend'),
((SELECT user_id FROM Users WHERE username='muzik_ruhu'), NULL, 'Yeni gitarımla ilk bestem. Dinlemek isteyenler profile bakabilir. #music #guitar'),
((SELECT user_id FROM Users WHERE username='gizem_ay'), NULL, 'Merkür retrosu bitiyor, rahat bir nefes alabiliriz. #astroloji'),
((SELECT user_id FROM Users WHERE username='john_doe'), NULL, 'SQL window functions are so powerful for analytics. #sql #analytics'),
((SELECT user_id FROM Users WHERE username='teknoloji_kurtu'), NULL, 'Kod yazarken müzik dinlemeyi sevenler burada mı? #coding #music'),
((SELECT user_id FROM Users WHERE username='baris_ozcan'), NULL, 'Tasarım odaklı düşünmek hayatın her alanında işe yarıyor. #designthinking')
ON CONFLICT DO NOTHING;

-- ============================================
-- 6. COMMENTS
-- ============================================

INSERT INTO Comments (post_id, user_id, content) VALUES
-- On Python post
((SELECT post_id FROM Posts WHERE content LIKE 'Just started learning%'), (SELECT user_id FROM Users WHERE username='mehmet_yilmaz'), 'Welcome to the community! Python is great.'),
((SELECT post_id FROM Posts WHERE content LIKE 'Just started learning%'), (SELECT user_id FROM Users WHERE username='teknoloji_kurtu'), 'Keep going, check out pandas library later.'),

-- On Istanbul post
((SELECT post_id FROM Posts WHERE content LIKE 'Visiting Istanbul%'), (SELECT user_id FROM Users WHERE username='john_doe'), 'Have fun! Eat some Baklava.'),
((SELECT post_id FROM Posts WHERE content LIKE 'Visiting Istanbul%'), (SELECT user_id FROM Users WHERE username='ayse_demir'), 'Bosphorus turu yapmayı unutma!'),

-- On Yemek post
((SELECT post_id FROM Posts WHERE content LIKE 'Bugün harika bir karnıyarık%'), (SELECT user_id FROM Users WHERE username='gizem_ay'), 'Ellerine sağlık, çok güzel görünüyor.'),
((SELECT post_id FROM Posts WHERE content LIKE 'Bugün harika bir karnıyarık%'), (SELECT user_id FROM Users WHERE username='selin_karaca'), 'Tarifi hemen deneyeceğim.'),

-- On AI post
((SELECT post_id FROM Posts WHERE content LIKE 'Yapay zeka modelleri%'), (SELECT user_id FROM Users WHERE username='can_turan'), 'Kesinlikle, ama etik konular da tartışılmalı.'),
((SELECT post_id FROM Posts WHERE content LIKE 'Yapay zeka modelleri%'), (SELECT user_id FROM Users WHERE username='teknoloji_kurtu'), 'OpenAI ve Google kapışması nereye gidecek bakalım.'),

-- On Game post
((SELECT post_id FROM Posts WHERE content LIKE 'League of Legends%'), (SELECT user_id FROM Users WHERE username='burak_celik'), 'T1 kazanır bu sene.'),
((SELECT post_id FROM Posts WHERE content LIKE 'League of Legends%'), (SELECT user_id FROM Users WHERE username='ali_yildiz'), 'G2 fanıyım ama zor.'),

-- On Book post
((SELECT post_id FROM Posts WHERE content LIKE 'Dostoyevski%'), (SELECT user_id FROM Users WHERE username='sinema_elestirmeni'), 'Evet, en iyi başlangıç kitabıdır.'),
((SELECT post_id FROM Posts WHERE content LIKE 'Dostoyevski%'), (SELECT user_id FROM Users WHERE username='baris_ozcan'), 'Karamazov Kardeşler de ağır ama iyidir.')
ON CONFLICT DO NOTHING;

-- ============================================
-- 7. LIKES (Bulk insert for popularity)
-- ============================================

-- Inserting likes manually for specific posts to create "Popular" posts
INSERT INTO PostLikes (post_id, user_id) VALUES
-- Python post likes
((SELECT post_id FROM Posts WHERE content LIKE 'Just started learning%'), (SELECT user_id FROM Users WHERE username='mehmet_yilmaz')),
((SELECT post_id FROM Posts WHERE content LIKE 'Just started learning%'), (SELECT user_id FROM Users WHERE username='teknoloji_kurtu')),
((SELECT post_id FROM Posts WHERE content LIKE 'Just started learning%'), (SELECT user_id FROM Users WHERE username='can_turan')),

-- Istanbul post likes
((SELECT post_id FROM Posts WHERE content LIKE 'Visiting Istanbul%'), (SELECT user_id FROM Users WHERE username='john_doe')),
((SELECT post_id FROM Posts WHERE content LIKE 'Visiting Istanbul%'), (SELECT user_id FROM Users WHERE username='ayse_demir')),
((SELECT post_id FROM Posts WHERE content LIKE 'Visiting Istanbul%'), (SELECT user_id FROM Users WHERE username='deniz_mavi')),
((SELECT post_id FROM Posts WHERE content LIKE 'Visiting Istanbul%'), (SELECT user_id FROM Users WHERE username='gizem_ay')),

-- AI post likes (Viral post)
((SELECT post_id FROM Posts WHERE content LIKE 'Yapay zeka modelleri%'), (SELECT user_id FROM Users WHERE username='teknoloji_kurtu')),
((SELECT post_id FROM Posts WHERE content LIKE 'Yapay zeka modelleri%'), (SELECT user_id FROM Users WHERE username='can_turan')),
((SELECT post_id FROM Posts WHERE content LIKE 'Yapay zeka modelleri%'), (SELECT user_id FROM Users WHERE username='baris_ozcan')),
((SELECT post_id FROM Posts WHERE content LIKE 'Yapay zeka modelleri%'), (SELECT user_id FROM Users WHERE username='john_doe')),
((SELECT post_id FROM Posts WHERE content LIKE 'Yapay zeka modelleri%'), (SELECT user_id FROM Users WHERE username='admin_user')),

-- Fitness post likes
((SELECT post_id FROM Posts WHERE content LIKE 'Bugünkü antrenman%'), (SELECT user_id FROM Users WHERE username='ali_yildiz')), -- Liking own post usually not counted but possible
((SELECT post_id FROM Posts WHERE content LIKE 'Bugünkü antrenman%'), (SELECT user_id FROM Users WHERE username='burak_celik')),
((SELECT post_id FROM Posts WHERE content LIKE 'Bugünkü antrenman%'), (SELECT user_id FROM Users WHERE username='deniz_mavi'))
ON CONFLICT DO NOTHING;
