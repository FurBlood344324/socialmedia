#!/usr/bin/env python3
"""
Generate comprehensive seed data for the social media application.
Run this script to generate a seed_data.sql file with comprehensive test data.
"""

import random
import time

# Turkish and English names for variety
FIRST_NAMES_TR = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Hasan", "Ibrahim", "Fatma", "Ayse", "Zeynep", "Emine",
                   "Burak", "Can", "Deniz", "Elif", "Gizem", "Hakan", "Ipek", "Kemal", "Leyla", "Murat",
                   "Recep", "Selin", "Yusuf", "Vildan"]
FIRST_NAMES_EN = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Chris", "Lisa", "Andrew", "Olivia",
                   "James", "Isabella", "Daniel", "Sophia", "Matthew", "Alex"]

LAST_NAMES_TR = ["Yilmaz", "Kaya", "Demir", "Celik", "Sahin", "Yildiz", "Ozturk", "Aydin", "Arslan", "Dogan",
                  "Kilic", "Polat", "Aksoy", "Korkmaz", "Ozdemir", "Kurt"]
LAST_NAMES_EN = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Wilson", "Rodriguez"]

# Bio texts - ASCII only for safety
BIOS = [
    "Yazilim ve teknoloji tutkunu 💻", "Fotografcilik ve seyahat 📷✈️", "Kitap kurdu 📚",
    "Spor ve saglikli yasam 💪", "Yemek yapma asigi 🍳", "Doga ve kamp 🏕️",
    "Sinema ve dizi tutkunu 🎬", "Girisimci ruhu ✨", "Hayat bir yolculuk 🌍", "Pozitif enerji 🌈",
    "Kod yazmayi seviyorum 👨‍💻", "Coffee addict ☕", "Tech enthusiast", "Digital nomad 🌎",
    "Startup founder", "Creative soul 🎭", "Music producer 🎹", "Content creator 📱",
    "Photographer 📸", "Traveler ✈️", "Fitness coach 🏋️", "AI researcher 🤖", "Minimalist yasam 🍃"
]

# Unique post templates - each generates unique content with post number embedded naturally
POST_TEMPLATES = [
    "Bugun {num}. kez kahve ictim, artik uyumam imkansiz! #coffee #energyboost",
    "Bu hafta {num} saat kod yazdim, verimli bir hafta oldu #coding #productivity",
    "Yeni bir proje baslattim, hedefim {num} gun icinde bitirmek #startup #motivation",
    "{num} gun once basladigim kitabi bitirdim, cok guzeldi! #reading #books",
    "Bugun {num} kilometre yuruyus yaptim, saglik icin hareket sart #fitness #health",
    "Bu ay {num} yeni teknoloji ogrendim, kendimi gelistirmeye devam #learning",
    "Yeni kahve tarifim: {num} dakikada hazirlaniyor #homemade #coffee",
    "Haftalik hedefim: {num} yeni sey denemek #goals #selfimprovement",
    "Bugunun pozitif enerjisi {num} yildizlik! #positivity #goodvibes",
    "Bu yil {num}. seyahatim icin hazirliklar basliyor #travel #adventure",
    "Yeni podcast buldum, {num} bolum dinledim bile #podcast #learning",
    "Meditasyona basladim, gunluk {num} dakika #meditation #mindfulness",
    "Bu hafta {num} toplanti yaptim, hepsi cok verimli gecti #meetings #teamwork",
    "Yeni bir hobi edindim: {num} gun once basladim #newhobby #fun",
    "Spor salonunda {num} set tamamladim, kas agrilarima hazir olmak #gym #workout",
    "Bu ay {num} yeni insan tanidum networking etkhinligi sayesinde #networking",
    "Sabah rutini: {num} dakikada gunumu planliyorum #morningroutine #planning",
    "Film onerisi: bu ay {num} film izledim, en iyisini paylasiyorum #movies #recommendation",
    "Yeni programlama dili ogreniyorum, {num} gun oldu baslayali #coding #newlanguage",
    "Dogada {num} saat gecirdim bu hafta sonu, harika hissediyorum #nature #weekend",
    "Yemek yapmak icin {num} dakika ayirdim, sonuc muhtesem oldu #cooking #homemade",
    "Bu gun {num} farli gorev tamamladim, super uretken bir gun #productive #tasklist",
    "Muzik calmak icin gunluk {num} dakika pratik yapiyorum #music #practice",
    "Yeni restoran denedim, {num} yildiz veriyorum #food #restaurant",
    "Sabah sporuna {num} gun once basladim, devMam edecegim #morning #exercise",
    "Bu hafta {num} makale okudum, bilgi paylasmak guzel #reading #knowledge",
    "Freelance projede {num} saat calistim bu ay #freelance #work",
    "Yeni bir kurs baslattim, {num} ders tamamladim #onlinelearning #education",
    "Fotografciliga basladim, {num} gun oldu baslayali #photography #hobby",
    "Bu ay {num} tane yeni tarif denedim, hepsi lezzetli #recipes #cooking",
]

# Comment texts - ASCII safe
COMMENT_CONTENTS = [
    "Harika bir paylasim!", "Cok dogru soyledin!", "Katiliyorum sana!",
    "Bu bilgi cok faydali, tesekkurler!", "Bunu denemek istiyorum!",
    "Muhtesem gorunuyor!", "Eline saglik!", "Cok guzel olmus!",
    "Bunu bilmiyordum, ogrenmis oldum!", "Harika bir deneyim olmus!",
    "Ben de ayni seyi dusunuyorum!", "Devamini bekliyoruz!",
    "Cok ilham verici!", "Supersin!", "Bravo!",
    "Excellent work!", "This is amazing!", "Love this!",
    "So inspiring!", "Great post!", "Thanks for sharing!"
]

# Community definitions
COMMUNITY_NAMES = [
    ("Yazilim Gelistiricileri", "Yazilim dunyasindan en guncel haberler ve tartismalar"),
    ("Fotografcilar Kulubu", "Fotograflarinizi paylasin ve tekniklerinizi gelistirin"),
    ("Kitap Severler", "Okumayi sevenler icin kitap onerileri ve tartismalar"),
    ("Yemek Tarifleri", "En lezzetli tarifler burada paylasiliyor"),
    ("Seyahat Tutkunlari", "Dunyayi kesfetmek isteyenler icin"),
    ("Fitness Merkezi", "Spor ve saglikli yasam hakkinda her sey"),
    ("Sinema Kulubu", "Film ve dizi tutkunu icin"),
    ("Muzik Dunyasi", "Muzik hakkinda her sey"),
    ("Oyun Evreni", "Oyuncular icin bulusma noktasi"),
    ("Startup Girisimcileri", "Girisimcilik ve is dunyasi"),
    ("Data Science TR", "Veri bilimi meraklilari toplulugu"),
    ("Mobile Developers", "iOS ve Android gelistirme"),
    ("DevOps Engineers", "CI/CD, Docker, Kubernetes ve daha fazlasi"),
    ("UI/UX Designers", "Tasarim odakli dusunce"),
    ("Crypto Traders", "Kripto para ve blockchain teknolojisi")
]

# Message contents - ASCII safe
MESSAGE_CONTENTS = [
    "Selam, nasilsin?", "Merhaba! Iyi misin?", "Hey, naber?",
    "Tesekkur ederim paylasimin icin!", "Guzel bir gun dilerim!",
    "Projeyle ilgili konusabilir miyiz?", "Vakit bulunca goruselim mi?",
    "Hey, how are you?", "Thanks for the help!", "Lets catch up soon!",
    "Great work on that project!", "Looking forward to it!",
    "Bu konuda sana sormak istedigim bir sey var", "Harika bir is cikarmissin!",
    "Ilginc bir fikrin var mi?", "Yakinda bulusalim", "Yardiinin icin tesekkurler!",
    "Can we discuss this?", "O konu hakkinda ne dusunuyorsun?"
]


def escape_sql(s):
    """Escape single quotes for SQL"""
    return s.replace("'", "''")


def generate_username(first, last, idx):
    """Generate a unique username"""
    patterns = [
        f"{first.lower()}{last.lower()}{idx}",
        f"{first.lower()}_{last.lower()}",
        f"{first.lower()}.{last.lower()}",
        f"{first.lower()}_{idx}"
    ]
    return patterns[idx % len(patterns)]


def generate_unique_post_content(post_number, user):
    """Generate unique post content using post number naturally embedded"""
    template = POST_TEMPLATES[post_number % len(POST_TEMPLATES)]
    # Use post_number to create unique content - embedded naturally in the text
    return template.format(num=post_number)


def generate_sql():
    lines = []
    
    lines.append("-- ============================================")
    lines.append("-- COMPREHENSIVE SEED DATA")
    lines.append("-- Generated automatically for testing all features")
    lines.append("-- ============================================")
    lines.append("")
    
    # Base tables
    lines.append("INSERT INTO Roles (role_name) VALUES ('admin'), ('moderator'), ('member') ON CONFLICT DO NOTHING;")
    lines.append("INSERT INTO PrivacyTypes (privacy_name) VALUES ('public'), ('private') ON CONFLICT DO NOTHING;")
    lines.append("INSERT INTO FollowStatus (status_name) VALUES ('pending'), ('accepted'), ('rejected') ON CONFLICT DO NOTHING;")
    lines.append("")
    
    # Generate users
    lines.append("-- ============================================")
    lines.append("-- USERS (50)")
    lines.append("-- ============================================")
    lines.append("")
    
    users = []
    password_hash = "scrypt:32768:8:1$ezOQvpqIxHxFtTlX$541a3d8877c11e90e7a20f705f39aff8a352c3de7349f1a0fc278937284528cfca2100d864e3866ac4c40331f1011c49ebd57f71172c2e2465de02a91a3bf263"
    timestamp_base = int(time.time())
    
    all_first_names = FIRST_NAMES_TR + FIRST_NAMES_EN
    all_last_names = LAST_NAMES_TR + LAST_NAMES_EN
    
    used_usernames = set()
    for i in range(50):
        first = random.choice(all_first_names)
        last = random.choice(all_last_names)
        username = generate_username(first, last, i)
        
        # Ensure unique username
        while username in used_usernames:
            username = f"{first.lower()}_{i}"
            if username in used_usernames:
                username = f"{first.lower()}{last.lower()}_{i}"
        used_usernames.add(username)
        
        email = f"{username}@example.com"
        bio = escape_sql(random.choice(BIOS))
        is_private = "TRUE" if i % 8 == 0 else "FALSE"
        avatar_url = f"http://localhost:5000/static/uploads/{username}_{timestamp_base + i}_default.svg"
        
        users.append(username)
        lines.append(f"INSERT INTO Users (username, email, password_hash, bio, is_private, profile_picture_url) VALUES ('{username}', '{email}', '{password_hash}', '{bio}', {is_private}, '{avatar_url}') ON CONFLICT DO NOTHING;")
    
    lines.append("")
    
    # Generate communities
    lines.append("-- ============================================")
    lines.append(f"-- COMMUNITIES ({len(COMMUNITY_NAMES)})")
    lines.append("-- ============================================")
    lines.append("")
    
    communities = []
    for i, (name, desc) in enumerate(COMMUNITY_NAMES):
        creator = users[i % len(users)]
        privacy = "public" if i % 5 != 0 else "private"
        communities.append(name)
        lines.append(f"INSERT INTO Communities (name, description, creator_id, privacy_id) VALUES ('{escape_sql(name)}', '{escape_sql(desc)}', (SELECT user_id FROM Users WHERE username='{creator}'), (SELECT privacy_id FROM PrivacyTypes WHERE privacy_name='{privacy}')) ON CONFLICT DO NOTHING;")
    
    lines.append("")
    
    # Generate community members (150+)
    lines.append("-- ============================================")
    lines.append("-- COMMUNITY MEMBERS (150+)")
    lines.append("-- ============================================")
    lines.append("")
    
    for idx, name in enumerate(communities):
        num_members = 10 + (idx % 12)
        for j in range(num_members):
            member = users[(idx * 7 + j) % len(users)]
            role = "moderator" if j < 3 else "member"
            lines.append(f"INSERT INTO CommunityMembers (community_id, user_id, role_id) VALUES ((SELECT community_id FROM Communities WHERE name='{escape_sql(name)}'), (SELECT user_id FROM Users WHERE username='{member}'), (SELECT role_id FROM Roles WHERE role_name='{role}')) ON CONFLICT DO NOTHING;")
    
    lines.append("")
    
    # Generate follows (LinkedIn-style mutual connections)
    lines.append("-- ============================================")
    lines.append("-- FOLLOWS (Mutual Connections - LinkedIn-style)")
    lines.append("-- ============================================")
    lines.append("")
    
    # Track created connections to avoid duplicates
    created_connections = set()
    
    for i, user in enumerate(users):
        num_connections = 6 + (i % 12)
        for j in range(num_connections):
            target_idx = (i + j + 1) % len(users)
            if target_idx != i:
                # Create a sorted tuple to represent the connection (bidirectional)
                connection_key = tuple(sorted([i, target_idx]))
                
                # Only create if not already created
                if connection_key not in created_connections:
                    created_connections.add(connection_key)
                    
                    # Most connections are accepted (mutual), some are pending
                    if j % 7 == 0:
                        # Pending request (only one direction)
                        lines.append(f"INSERT INTO Follows (follower_id, following_id, status_id) VALUES ((SELECT user_id FROM Users WHERE username='{user}'), (SELECT user_id FROM Users WHERE username='{users[target_idx]}'), (SELECT status_id FROM FollowStatus WHERE status_name='pending')) ON CONFLICT DO NOTHING;")
                    else:
                        # Mutual connection (both directions, accepted)
                        lines.append(f"INSERT INTO Follows (follower_id, following_id, status_id) VALUES ((SELECT user_id FROM Users WHERE username='{user}'), (SELECT user_id FROM Users WHERE username='{users[target_idx]}'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')) ON CONFLICT DO NOTHING;")
                        lines.append(f"INSERT INTO Follows (follower_id, following_id, status_id) VALUES ((SELECT user_id FROM Users WHERE username='{users[target_idx]}'), (SELECT user_id FROM Users WHERE username='{user}'), (SELECT status_id FROM FollowStatus WHERE status_name='accepted')) ON CONFLICT DO NOTHING;")
    
    lines.append("")
    
    # Generate posts with UNIQUE content (number embedded naturally)
    lines.append("-- ============================================")
    lines.append("-- POSTS (200+)")
    lines.append("-- ============================================")
    lines.append("")
    
    # Store post data for likes/comments matching - use first 30 chars as unique key
    post_data = []  # List of (match_prefix, user)
    post_number = 0
    
    for i, user in enumerate(users):
        num_posts = 4 + (i % 5)
        for j in range(num_posts):
            post_number += 1
            content = generate_unique_post_content(post_number, user)
            # Use first 30 characters as unique match prefix
            match_prefix = content[:30]
            post_data.append((match_prefix, user))
            
            if j % 3 == 0 and communities:
                community = communities[j % len(communities)]
                lines.append(f"INSERT INTO Posts (user_id, community_id, content) VALUES ((SELECT user_id FROM Users WHERE username='{user}'), (SELECT community_id FROM Communities WHERE name='{escape_sql(community)}'), '{escape_sql(content)}') ON CONFLICT DO NOTHING;")
            else:
                lines.append(f"INSERT INTO Posts (user_id, content) VALUES ((SELECT user_id FROM Users WHERE username='{user}'), '{escape_sql(content)}') ON CONFLICT DO NOTHING;")
    
    lines.append("")
    
    # Generate comments using prefix matching
    lines.append("-- ============================================")
    lines.append("-- COMMENTS (400+)")
    lines.append("-- ============================================")
    lines.append("")
    
    for idx, (match_prefix, author) in enumerate(post_data[:100]):
        num_comments = 3 + (idx % 5)
        for j in range(num_comments):
            commenter = users[(idx + j + 5) % len(users)]
            comment_text = escape_sql(COMMENT_CONTENTS[j % len(COMMENT_CONTENTS)])
            # Use LIKE with first 30 chars to find post
            lines.append(f"INSERT INTO Comments (post_id, user_id, content) VALUES ((SELECT post_id FROM Posts WHERE content LIKE '{escape_sql(match_prefix)}%' LIMIT 1), (SELECT user_id FROM Users WHERE username='{commenter}'), '{comment_text}') ON CONFLICT DO NOTHING;")
    
    lines.append("")
    
    # Generate likes using prefix matching
    lines.append("-- ============================================")
    lines.append("-- LIKES (500+)")
    lines.append("-- ============================================")
    lines.append("")
    
    for idx, (match_prefix, author) in enumerate(post_data[:80]):
        num_likes = 5 + (idx % 10)
        for j in range(num_likes):
            liker = users[(idx + j + 3) % len(users)]
            # Use LIKE with first 30 chars to find post
            lines.append(f"INSERT INTO PostLikes (post_id, user_id) VALUES ((SELECT post_id FROM Posts WHERE content LIKE '{escape_sql(match_prefix)}%' LIMIT 1), (SELECT user_id FROM Users WHERE username='{liker}')) ON CONFLICT DO NOTHING;")
    
    lines.append("")
    
    # Generate messages (200+)
    lines.append("-- ============================================")
    lines.append("-- MESSAGES (200+)")
    lines.append("-- ============================================")
    lines.append("")
    
    for i in range(25):
        for j in range(4):
            sender = users[i]
            receiver = users[(i + j + 1) % len(users)]
            if sender != receiver:
                for k in range(4):
                    msg = escape_sql(MESSAGE_CONTENTS[k % len(MESSAGE_CONTENTS)])
                    s, r = (sender, receiver) if k % 2 == 0 else (receiver, sender)
                    lines.append(f"INSERT INTO Messages (sender_id, receiver_id, content) VALUES ((SELECT user_id FROM Users WHERE username='{s}'), (SELECT user_id FROM Users WHERE username='{r}'), '{msg}') ON CONFLICT DO NOTHING;")
    
    lines.append("")
    lines.append("-- END OF SEED DATA")
    
    return "\n".join(lines)


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    sql = generate_sql()
    with open("seed_data.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"Generated seed_data.sql with {len(sql.splitlines())} lines")
