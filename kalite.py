import streamlit as st
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image
from datetime import datetime
import os
import mysql.connector
import time
import logging
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()  # Veritabanı bilgilerini burada güvenli bir şekilde saklayabilirsiniz.

# Veritabanı bağlantısı için sınıf oluşturma
class DatabaseConnection:
    def __init__(self):
        # .env dosyasından alınan bilgiler
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "duyar_metal_db")  # Veritabanı adını .env'den al

        self.conn = None

    def connect(self):
        """Veritabanı bağlantısını başlat."""
        if self.conn is None:
            try:
                self.conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            except mysql.connector.Error as err:
                logging.error(f"Veritabanı bağlantısı başarısız: {err}")
                raise

    def insert_data(self, urun_tanim, kalite, firma, sertifika_no, foto_path):
        """Veritabanına yeni veri ekleme."""
        self.connect()
        cursor = self.conn.cursor()
        insert_query = """
            INSERT INTO sertifikalar (urun_tanim, kalite, firma, sertifika_no, foto_path)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (urun_tanim, kalite, firma, sertifika_no, foto_path))
        self.conn.commit()
        cursor.close()

    def get_data(self):
        """Veritabanından veri çek."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sertifikalar ORDER BY eklenme_tarihi DESC")  # Veritabanını sorgula
        data = cursor.fetchall()  # Veriyi çek
        cursor.close()
        return data

    def close_connection(self):
        """Veritabanı bağlantısını kapat."""
        if self.conn:
            self.conn.close()

# Streamlit arayüzü
st.title('Duyar Metal Kalite Sertifikaları Yönetim Sistemi')

# Veri ekleme kısmı
st.header('Yeni Ürün Ekle')

urun_tanim = st.text_input('Ürün Tanımı:')
kalite = st.text_input('Kalite:')
firma = st.text_input('Firma Adı:')
sertifika_no = st.text_input('Sertifika No:')
sertifika_resmi = st.file_uploader("Sertifika Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])

# Sertifika fotoğrafı yüklenmişse, dosya sistemine kaydedelim
image_folder = 'C:/deneme/SertifikaFotoğrafları'
os.makedirs(image_folder, exist_ok=True)

if sertifika_resmi:
    image_path = os.path.join(image_folder, f"{sertifika_no}.jpg")
    with open(image_path, "wb") as f:
        f.write(sertifika_resmi.getbuffer())

# Yeni ürün eklemek için buton
if st.button('Ürün Ekle'):
    if urun_tanim and kalite and firma and sertifika_no:
        # Veritabanına veri ekle
        db_connection = DatabaseConnection()
        db_connection.insert_data(urun_tanim, kalite, firma, sertifika_no, image_path)
        db_connection.close_connection()

        st.success('Yeni ürün başarıyla eklendi ve veritabanına kaydedildi.')

# Arama / Filtreleme Kısmı
st.header('Verileri Ara')

# Veritabanındaki verileri güncellemek için buton
if st.button("Veri Güncelle"):
    db_connection = DatabaseConnection()
    try:
        data = db_connection.get_data()
        db_connection.close_connection()

        # Veriyi Streamlit üzerinden göster
        st.write(data)
    except Exception as e:
        st.error(f"Veri güncelleme işlemi başarısız: {e}")