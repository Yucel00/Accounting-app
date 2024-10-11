import sqlite3
import tkinter as tk
from tkinter import messagebox
from grafik import *
from datetime import date
BUGUN = date.today()
class Database(tk.Tk):
    def __init__(self):
        self.conn = sqlite3.connect('hairstyle.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Gelir tablosu
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gelir (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tarih TEXT,
                        gun TEXT,
                        tutar FLOAT,
                        calisan_id INTEGER,
                        odeme_yontemi_id INTEGER,
                        FOREIGN KEY (calisan_id) REFERENCES calisan(id),
                        FOREIGN KEY (odeme_yontemi_id) REFERENCES odeme_yontemleri(id)
                        )''')

        # Gider tablosu
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gider (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tarih TEXT,
                        gun TEXT,
                        tutar FLOAT,
                        calisan_id INTEGER,
                        odeme_yontemi_id INTEGER,
                        FOREIGN KEY (calisan_id) REFERENCES calisan(id),
                        FOREIGN KEY (odeme_yontemi_id) REFERENCES odeme_yontemleri(id)
                        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS calisan(
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            ad TEXT,
                            soyad TEXT,
                            maas FLOAT
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS odeme_yontemleri(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            odeme TEXT
                            
                            )''')
        

    def aralik_al(self, tarih1, tarih2):
        query1 = """
            SELECT tutar FROM gelir
            WHERE tarih BETWEEN ? AND ?
        """
        self.cursor.execute(query1, (tarih1, tarih2))
        gelirler = self.cursor.fetchall()
        
        query2 = """
            SELECT tutar FROM gider
            WHERE tarih BETWEEN ? AND ?
        """
        self.cursor.execute(query2, (tarih1, tarih2))
        giderler = self.cursor.fetchall()
        
        gelir_toplam = sum([gelir[0] for gelir in gelirler])
        gider_toplam = sum([gider[0] for gider in giderler])
    
        return gelir_toplam, gider_toplam


    def odeme_yontemleri(self,liste):
        query_check = "SELECT * FROM odeme_yontemleri WHERE odeme = ?"
        query_insert = "INSERT INTO odeme_yontemleri (odeme) VALUES (?)"

        for odeme in liste:
            # Ödeme yöntemi veritabanında var mı kontrol et
            self.cursor.execute(query_check, (odeme,))
            sonuc = self.cursor.fetchone()

            if sonuc:
                pass
            else:
                # Ödeme yöntemini ekle
                self.cursor.execute(query_insert, (odeme,))
                self.conn.commit()


    def odeme_id_al(self,odeme_adi):
        query = """
            SELECT id FROM odeme_yontemleri 
            WHERE odeme = ?
        """
        self.cursor.execute(query, (odeme_adi,))
        return self.cursor.fetchone()[0]
    def calisan_id_al(self,isim,soyisim):
        print(isim)
        try:
            query = """
            SELECT id FROM calisan
            WHERE ad = ? AND soyad = ?
            """
            
            self.cursor.execute(query, (isim,soyisim))
            return self.cursor.fetchone()[0]
        except:
            messagebox.showerror("Hata","Bu Çalışan Çıkarılmış")
            

    def kar_al(self, tarih1, tarih2):
        gelir_toplam, gider_toplam = self.aralik_al(tarih1, tarih2)
        kar_toplam = gelir_toplam - gider_toplam
        return kar_toplam

            
    def calisan_ekle(self,ad,soyad):
        ad=ad.title()
        soyad=soyad.title()
        ad=ad.strip()
        soyad=soyad.strip()
        check_query = "SELECT COUNT(*) FROM calisan WHERE ad = ? AND soyad = ?"
        self.cursor.execute(check_query, (ad, soyad))
        result = self.cursor.fetchone()
        
        if result[0]==0:
            query = """
                INSERT INTO calisan (ad,soyad) 
                VALUES (?,?)
                """
            
            self.cursor.execute(query,(ad,soyad))
            messagebox.showinfo("Başarılı", f"{ad} {soyad} başarıyla eklendi!")
        else:
             messagebox.showwarning("Uyarı", "Bu isimde bir çalışan zaten var.")
             return
    def calisan_cikar(self,ad,soyad):
        check_query = "SELECT COUNT(*) FROM calisan WHERE id = ?"
        ad = ad.title()
        soyad = soyad.title()
        
        id = self.calisan_id_al(ad, soyad)

        # Tek bir parametre demet olarak iletiliyor
        self.cursor.execute(check_query, (id,))
        result = self.cursor.fetchone()
       
        if result[0]==1:
            print("Girdik")
            query = """
                DELETE FROM calisan WHERE id = ?
                """
            ad=ad.title()
            soyad=soyad.title()
            id=self.calisan_id_al(ad,soyad)
            self.cursor.execute(query,(id,))
            messagebox.showinfo("Başarılı", f"{ad} {soyad} başarıyla çıkarıldı!")
        else:
             messagebox.showwarning("Uyarı", "Bu isimde bir çalışan yok.")
    
    def liste_olustur(self):
        query = "SELECT ad,soyad FROM calisan "
        self.cursor.execute(query)
        liste = self.cursor.fetchall()
        yeni_liste=[""]
        for i in liste:
            yeni_liste.insert(0,f"{i[0]} {i[1]}")
        self.conn.commit()
        return yeni_liste
    
    #açılır pencerede göstermek için
    def calisan_bazli_rapor(self, tarih1, tarih2):
        query = """
            SELECT c.ad || ' ' || c.soyad as calisan, 
                   SUM(CASE WHEN o.odeme = 'IBAN' THEN g.tutar ELSE 0 END) as gelir_iban,
                   SUM(CASE WHEN o.odeme = 'Nakit' THEN g.tutar ELSE 0 END) as gelir_nakit,
                   SUM(CASE WHEN o.odeme = 'Kredi Kartı' THEN g.tutar ELSE 0 END) as gelir_kart,
                   (SELECT SUM(tutar) FROM gider WHERE calisan_id = c.id AND tarih BETWEEN ? AND ?) as toplam_gider 
            FROM gelir g 
            JOIN calisan c ON g.calisan_id = c.id 
            JOIN odeme_yontemleri o ON g.odeme_yontemi_id = o.id
            WHERE g.tarih BETWEEN ? AND ? 
            GROUP BY c.ad, c.soyad
        """
        self.cursor.execute(query, (tarih1, tarih2, tarih1, tarih2))
        return self.cursor.fetchall()


    def geri_al(self,listbox):
        try:
            selected_index = listbox.curselection()
            if selected_index:
                # İndeksine göre seçili elemanın değerini al
                selected_value = listbox.get(selected_index)
                selected_value=selected_value.split(" ")
                tarih=selected_value[0]
                isim=selected_value[1]
                soyisim=selected_value[2]
                calisan_id=self.calisan_id_al(isim,soyisim)
                if selected_value[3]=="Kredi":
                    odeme_id=self.odeme_id_al(f"{selected_value[3]} {selected_value[4]}")
                    tutar=selected_value[6]
                    tablo=selected_value[8].lower()
                else:
                    odeme_id=self.odeme_id_al(selected_value[3])
                    tutar=selected_value[5]
                    tablo=selected_value[7].lower()
                query=f"""SELECT tutar from {tablo} WHERE tarih = ? AND calisan_id = ? AND odeme_yontemi_id = ? """
                para=self.cursor.execute(query,(tarih,calisan_id,odeme_id)).fetchone()[0]
                tutar=tutar.replace(".","")
                para=para-float(tutar)
                self.cursor.execute(f"UPDATE {tablo} SET tutar = ? WHERE tarih = ? AND calisan_id = ? AND odeme_yontemi_id = ?",(para,tarih,calisan_id,odeme_id))  
                
                listbox.delete(selected_index)              
                listbox.insert(0,f"{tarih} {isim} {soyisim} {selected_value[3]} {tutar} TL geri alındı")   
                  
                                  
                self.conn.commit()
               
        except:
            messagebox.showinfo("Eror","Bu İşlem Geri Alınamaz")
                 
    def maas_ekle(self,id,maas):
        query_null_check = "UPDATE calisan SET maas = 0 WHERE id = ? AND maas IS NULL"
        self.cursor.execute(query_null_check, (id,))
        
        
        query_update = "UPDATE calisan SET maas = ? WHERE id = ?"
        self.cursor.execute(query_update, (maas, id))
        
       
        self.conn.commit()


    def maas_al(self,id):
        query="""
        SELECT maas from calisan where id = ? 
"""
        self.cursor.execute(query,(id))
    def close(self):
        self.conn.close()