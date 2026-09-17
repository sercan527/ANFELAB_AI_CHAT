from flask import Blueprint, request, jsonify, render_template
from app.database import lead_ekle, tum_leadler
from app.services.ai_service import ai_yanit_uret


main_bp = Blueprint('main', __name__)

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