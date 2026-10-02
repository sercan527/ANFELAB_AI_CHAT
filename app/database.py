import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        db_path = current_app.config['DATABASE_URL'].replace('sqlite:///', '')
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Her istek sonunda veritabanı bağlantısını kapatır."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        
        # Leads Tablosu
        db.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mesaj TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ziyaretçi Sayacı Tablosu (YENİ EKLENDİ)
        db.execute('''
            CREATE TABLE IF NOT EXISTS istatistikler (
                id INTEGER PRIMARY KEY,
                ziyaret_sayisi INTEGER DEFAULT 0
            )
        ''')
        
        # Eğer istatistikler tablosu boşsa, ilk kaydı 0 olarak oluştur
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM istatistikler WHERE id = 1')
        row = cursor.fetchone()
        if row['count'] == 0:
            cursor.execute('INSERT INTO istatistikler (id, ziyaret_sayisi) VALUES (1, 0)')
            
        db.commit()


def lead_ekle(isim, telefon, mesaj=""):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO leads (isim, telefon, mesaj) VALUES (?, ?, ?)',
        (isim, telefon, mesaj)
    )
    db.commit()
    return cursor.lastrowid


def tum_leadler():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, isim, telefon, mesaj, tarih FROM leads ORDER BY tarih DESC')
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({
            'id': row['id'],
            'isim': row['isim'],
            'telefon': row['telefon'],
            'mesaj': row['mesaj'],
            'tarih': str(row['tarih'])
        })
    return result

def ziyaretci_sayisini_artir():
    db = get_db()
    cursor = db.cursor()
    
    # Mevcut sayıyı 1 artır
    cursor.execute('UPDATE istatistikler SET ziyaret_sayisi = ziyaret_sayisi + 1 WHERE id = 1')
    db.commit()
    
    # Güncel sayıyı çekip döndür
    cursor.execute('SELECT ziyaret_sayisi FROM istatistikler WHERE id = 1')
    row = cursor.fetchone()
    
    return row['ziyaret_sayisi']