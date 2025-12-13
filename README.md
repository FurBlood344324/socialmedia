# 🌐 Social Media Project

Flask (Backend) ve Next.js (Frontend) teknolojileri kullanılarak geliştirilmiş, PostgreSQL veritabanı altyapısına sahip modern bir sosyal medya uygulamasıdır.

Bu proje, kullanıcıların profil oluşturması, gönderi paylaşması, yorum yapması, topluluklara katılması ve diğer kullanıcılarla etkileşime girmesi için gerekli temel özellikleri sağlar.

---

## 🚀 Kurulum Rehberi

Bu projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla takip edin.

### 📋 Gereksinimler

Kuruluma başlamadan önce aşağıdaki araçların bilgisayarınızda yüklü olduğundan emin olun:

-   **Git**: Projeyi indirmek için.
-   **Python 3.11+**: Backend için.
-   **Node.js 18+ & npm**: Frontend için.
-   **PostgreSQL 14+**: Veritabanı için.

---

### 1. Adım: Projeyi Bilgisayarınıza İndirin

Terminal veya komut istemcisini açın ve projeyi klonlayın:

```bash
git clone <repo-url>
cd SocialMediaProject
```

---

### 2. Adım: Python Ortamının Kurulumu (Backend)

**⚠️ ÖNEMLİ NOT:** Backend ile ilgili tüm kurulum ve çalıştırma işlemleri `backend` klasörü altında yapılmalıdır.

İşletim sisteminize uygun adımları takip edin:

#### 🐧 Linux ve 🍎 macOS Kullanıcıları (pyenv ile)

Bu projede Python sürüm yönetimi için **pyenv** kullanılması önerilir.

1.  Backend klasörüne gidin:
    ```bash
    cd backend
    ```

2.  Python 3.11.14 sürümünü yükleyin (Eğer yüklü değilse):
    ```bash
    pyenv install 3.11.14
    ```

3.  `socialmedia-env` adında bir sanal ortam oluşturun:
    ```bash
    pyenv virtualenv 3.11.14 socialmedia-env
    ```

4.  Bu klasör için yerel olarak bu ortamı tanımlayın:
    ```bash
    pyenv local socialmedia-env
    ```
    *(Artık bu klasöre her girdiğinizde `socialmedia-env` otomatik aktif olacaktır.)*

5.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

#### 🪟 Windows Kullanıcıları (venv ile)

Windows kullanıcıları için standart `venv` modülü kullanılacaktır.

1.  Backend klasörüne gidin:
    ```bash
    cd backend
    ```

2.  Sanal ortam oluşturun:
    ```powershell
    python -m venv venv
    ```

3.  Sanal ortamı aktifleştirin:
    *   **PowerShell:**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **CMD:**
        ```cmd
        .\venv\Scripts\activate.bat
        ```

4.  Gerekli kütüphaneleri yükleyin:
    ```powershell
    pip install -r requirements.txt
    ```

---

### 3. Adım: Veritabanı Kurulumu

PostgreSQL servinizin çalıştığından emin olun ve bir veritabanı oluşturun.

1.  Veritabanını ve kullanıcıyı oluşturun (psql veya pgAdmin kullanabilirsiniz):

    ```sql
    CREATE DATABASE social_media_db;
    CREATE USER your_user WITH PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE social_media_db TO your_user;
    -- Şema yetkileri için (gerekirse):
    GRANT ALL ON SCHEMA public TO your_user;
    ```

2.  **Environment Dosyasını Hazırlayın:**

    `backend` klasörü içerisindeyken `.env.example` dosyasını kopyalayarak `.env` dosyası oluşturun:

    ```bash
    # Linux/Mac
    cp .env.example .env

    # Windows
    copy .env.example .env
    ```

    `.env` dosyasını bir metin editörü ile açın ve veritabanı bilgilerinizi girin:

    ```env
    DATABASE_HOST=localhost
    DATABASE_PORT=5432
    DATABASE_NAME=social_media_db
    DATABASE_USER=your_user      # Oluşturduğunuz kullanıcı adı
    DATABASE_PASSWORD=your_password # Oluşturduğunuz şifre
    SECRET_KEY=your-super-secret-key
    JWT_SECRET_KEY=your-jwt-secret-key
    ```

> **Not:** Veritabanı tabloları, uygulama ilk kez çalıştırıldığında otomatik olarak oluşturulacaktır (`init.sql` kullanılır). Sizin manuel olarak tablo oluşturmanıza gerek yoktur.

---

### 4. Adım: Projeyi Başlatma

#### Backend'i Başlatma

Backend sunucusu API isteklerini karşılar.

1.  `backend` klasöründe olduğunuza ve sanal ortamın aktif olduğuna emin olun (`(socialmedia-env)` veya `(venv)` ibaresini görmelisiniz).

    ```bash
    # Eğer root dizindeyseniz:
    cd backend
    ```

2.  Uygulamayı başlatın:
    ```bash
    python app.py
    ```

    Sunucu `http://localhost:5000` adresinde çalışmaya başlayacaktır.

#### 🐍 Kullanılabilir Komutlar (Backend)

**⚠️ ÖNEMLİ:** Bu komutların hepsi `backend` klasörü altında çalıştırılmalıdır.

| Komut | Açıklama |
|-------|----------|
| `python app.py` | Backend sunucusunu başlatır. |
| `python reset_db.py` | Veritabanını sıfırlar ve `init.sql` ile yeniden oluşturur. (Dikkat: Tüm veriler silinir!) |
| `python run_all_tests.py` | Backend testlerini çalıştırır. |

#### Frontend'i Başlatma

Kullanıcı arayüzünü başlatmak için yeni bir terminal penceresi açın.

1.  `frontend` klasörüne gidin:
    ```bash
    cd frontend
    ```

2.  Paketleri yükleyin (İlk kurulumda):
    ```bash
    npm install
    ```

3.  **Environment Dosyasını Hazırlayın:**

    `frontend` klasörü içerisindeyken `.env.example` dosyasını kopyalayarak `.env` dosyası oluşturun:
    
    ```bash
    # Linux/Mac
    cp .env.example .env

    # Windows
    copy .env.example .env
    ```

    Dosya içeriğini kontrol edin (Varsayılan olarak `http://localhost:5000` ayarlıdır):
    
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:5000
    ```

4.  Geliştirme sunucusunu başlatın:
    ```bash
    npm run dev
    ```

    Frontend uygulaması genellikle `http://localhost:3000` adresinde yayına başlar.

#### 📜 Kullanılabilir Komutlar (Frontend)

`frontend` klasörü içerisindeyken aşağıdaki komutları kullanabilirsiniz:

| Komut | Açıklama |
|-------|----------|
| `npm run dev` | Geliştirme sunucusunu başlatır (Hot Reload aktif). |
| `npm run build` | Uygulamayı prodüksiyon için derler. |
| `npm run start` | Derlenmiş uygulamayı başlatır. |
| `npm run lint` | Kod hatalarını kontrol eder (ESLint). |
| `npm run format` | Kodu otomatik olarak düzenler (Prettier). |

---

## 📁 Proje Yapısı

```
SocialMediaProject/
├── backend/           # Python/Flask Backend (Tüm backend işlemleri burada)
│   ├── api/           # API Controller, Service, Repository katmanları
│   ├── app.py         # Backend giriş noktası
│   └── ...
├── database/          # SQL şemaları ve seed verileri
└── frontend/          # Next.js Frontend uygulaması
```

---

## 🛠️ Geliştirici Notları

*   Backend'e yeni bir paket eklerseniz `pip freeze > requirements.txt` ile bağımlılık listesini güncellemeyi unutmayın.
*   Veritabanı şemasında değişiklik yaparsanız `database` klasörünü güncel tutun.
