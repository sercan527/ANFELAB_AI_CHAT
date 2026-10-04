from flask import Blueprint, request, jsonify, render_template

# tum_kullanicilar import listesine eklendi
from app.database import lead_ekle, tum_leadler, get_db, ziyaretci_sayisini_artir, kullanici_ekle_db, tum_kullanicilar
from app.services.ai_service import ai_yanit_uret

main_bp = Blueprint('main', __name__)


# 1. HER SAYFA AÇILDIĞINDA SAYACI ARTIRAN APİ (masterPage.js tetikleyecek)
@main_bp.route('/api/ziyaret', methods=['GET'])
def ziyaret_sayaci():
    try:
        # Bu fonksiyon database.py içinden çağrılıp sayıyı DB'de 1 artırır
        guncel_sayi = ziyaretci_sayisini_artir()
        return jsonify({"ziyaretci_sayisi": guncel_sayi}), 200
    except Exception as e:
        return jsonify({"hata": f"Sayaç artırma hatası: {str(e)}"}), 500


# 2. SADECE SAYIYI OKUYAN APİ (Wix Yönetim Paneli tetikleyecek)
@main_bp.route('/api/istatistik', methods=['GET'])
def istatistik_getir():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT ziyaret_sayisi FROM istatistikler WHERE id = 1')
        row = cursor.fetchone()
        
        # Eğer tablo boşsa 0 döndür
        sayi = row['ziyaret_sayisi'] if row else 0
        return jsonify({"ziyaretci_sayisi": sayi}), 200
    except Exception as e:
        return jsonify({"hata": f"İstatistik okuma hatası: {str(e)}"}), 500


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "durum": "saglikli",
        "sistem": "ANFE LAB SmartLead AI"
    }), 200


@main_bp.route('/api/sohbet', methods=['POST'])
def sohbet_api():
    try:
        data = request.get_json() or {}
        kullanici_mesaji = data.get('mesaj', '').strip()
        sohbet_gecmisi = data.get('gecmis', [])
        
        if not kullanici_mesaji:
            return jsonify({"hata": "Mesaj alanı boş olamaz."}), 400
            
        yanit = ai_yanit_uret(kullanici_mesaji, sohbet_gecmisi)
        return jsonify({"yanit": yanit}), 200
        
    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}"}), 500


@main_bp.route('/api/leads', methods=['GET', 'POST'])
def leads_api():
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            isim = data.get('isim', '').strip()
            telefon = data.get('telefon', '').strip()
            mesaj = data.get('mesaj', '').strip()
            
            if not isim or not telefon:
                return jsonify({"hata": "İsim ve telefon alanları zorunludur."}), 400
                
            lead_id = lead_ekle(isim, telefon, mesaj)
            return jsonify({
                "durum": "basarili",
                "id": lead_id,
                "mesaj": "Müşteri adayı başarıyla kaydedildi."
            }), 201
            
        elif request.method == 'GET':
            kayitlar = tum_leadler()
            return jsonify({"leads": kayitlar}), 200
            
    except Exception as e:
        return jsonify({"hata": f"Veritabanı/Sunucu hatası: {str(e)}"}), 500


@main_bp.route('/api/kullanici_ekle', methods=['POST'])
def kullanici_ekle():
    try:
        data = request.json
        k_adi = data.get('kullanici_adi')
        sifre = data.get('sifre')
        email = data.get('email', '') 

        if not k_adi or not sifre:
            return jsonify({"hata": "Kullanıcı adı ve şifre zorunludur"}), 400

        # Mevcut app.db yapına uygun fonksiyonu kullanıyoruz
        kullanici_ekle_db(k_adi, sifre, email)

        return jsonify({"mesaj": "Kullanıcı başarıyla kaydedildi!"}), 201

    except Exception as e:
        return jsonify({"hata": f"Kayıt hatası: {str(e)}"}), 500


# --- YENİ EKLENEN: GİRİŞ (LOGIN) API'Sİ ---
@main_bp.route('/api/giris', methods=['POST'])
def kullanici_giris():
    try:
        data = request.json
        k_adi = data.get('kullanici_adi')
        sifre = data.get('sifre')

        if not k_adi or not sifre:
            return jsonify({"hata": "Kullanıcı adı ve şifre zorunludur"}), 400

        # Veritabanında kullanıcıyı ara
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?', (k_adi, sifre))
        kullanici = cursor.fetchone()

        if kullanici:
            return jsonify({"durum": "basarili", "mesaj": "Giriş onaylandı"}), 200
        else:
            return jsonify({"hata": "Kullanıcı adı veya şifre hatalı!"}), 401

    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}"}), 500


# --- YENİ EKLENEN: KULLANICILARI LİSTELEME API'Sİ (Wix 2. Tablo İçin) ---
@main_bp.route('/api/kullanicilar', methods=['GET'])
def kullanicilar_getir():
    try:
        kayitlar = tum_kullanicilar()
        return jsonify({"kullanicilar": kayitlar}), 200
    except Exception as e:
        return jsonify({"hata": f"Kullanıcı verileri okunamadı: {str(e)}"}), 500