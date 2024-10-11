import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from database import Database
from PIL import Image, ImageDraw, ImageFont, ImageTk
from util import *

class GelirGosterApp(tk.Toplevel):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.title("Çalışan Gelir Göster")
        window_height = 350
        window_width = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.geometry(f'{window_width}x{window_height}+{x_cordinate}+{y_cordinate}')
        self.configure(bg="#33373d")
        self.db=Database()
        # Başlık rengi
        self.title_frame = tk.Frame(self, bg="#EB1B5A", pady=10)
        self.title_frame.pack(fill=tk.X)
        self.title_label = tk.Label(self.title_frame, text="Çalışan Gelir Göster", bg="#EB1B5A", fg="#E0E0E0", font=("Bold", 15))
        self.title_label.pack()

        # İçerik frame
        self.content_frame = tk.Frame(self, bg="#33373d", padx=20, pady=20)
        self.content_frame.pack(expand=True, fill=tk.BOTH)

        # Çalışan seçimi için dropdown menü
        self.label = tk.Label(self.content_frame, text="Çalışan Seç:", bg="#33373d", fg="#FFFFFF", font=("Bold", 15))
        self.label.grid(row=0, column=0, sticky="w", pady=5)

        self.calisan_var = tk.StringVar()
        self.calisan_dropdown = ttk.Combobox(self.content_frame, textvariable=self.calisan_var, values=self.database.liste_olustur())
        self.calisan_dropdown.grid(row=0, column=1, pady=5, sticky="ew")

        # Tarih seçimi için tarih aralığı widget'ları
        self.start_date_label = tk.Label(self.content_frame, text="Başlangıç Tarihi:", bg="#33373d", fg="#FFFFFF", font=("Bold", 15))
        self.start_date_label.grid(row=1, column=0, sticky="w", pady=5)
        self.start_date_entry = DateEntry(self.content_frame, background='darkblue', foreground='white', borderwidth=2, font=("Bold", 12), locale="tr_TR")
        self.start_date_entry.grid(row=1, column=1, pady=5, sticky="ew")

        self.end_date_label = tk.Label(self.content_frame, text="Bitiş Tarihi:", bg="#33373d", fg="#FFFFFF", font=("Bold", 15))
        self.end_date_label.grid(row=2, column=0, sticky="w", pady=5)
        self.end_date_entry = DateEntry(self.content_frame, background='darkblue', foreground='white', borderwidth=2, font=("Bold", 12), locale="tr_TR")
        self.end_date_entry.grid(row=2, column=1, pady=5, sticky="ew")

        # Butonlar
        self.f11 = ImageTk.PhotoImage(Image.open("images/Frame12.png"))
        self.f13 = ImageTk.PhotoImage(Image.open("images/Frame14.png"))
        self.f7 = ImageTk.PhotoImage(Image.open("images/Frame7.png"))
        self.show_button = tk.Button(self.content_frame, image=self.f11, border=0, cursor='hand2', highlightthickness=0,  background=bg_color,command=self.geliri_goster)
        self.show_button.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")

        self.calculate_salary_button = tk.Button(self.content_frame,image=self.f13, border=0, cursor='hand2', highlightthickness=0,  background=bg_color, command=self.maas_hesapla)
        self.calculate_salary_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # Satır genişliği ayarları
        self.content_frame.grid_columnconfigure(1, weight=1)

    def geliri_goster(self):
        # Seçilen çalışanın ad ve soyadını alır
        secilen_calisan = self.calisan_var.get()
        secilen_calisan=secilen_calisan.split()
        if not secilen_calisan:
            tk.messagebox.showwarning("Uyarı", "Lütfen bir çalışan seçin.")
            return

        if len(secilen_calisan)>2:
            ad = " ".join(secilen_calisan[:-1])
            soyad=secilen_calisan[-1]
        else:
            ad=secilen_calisan[0]
            soyad=secilen_calisan[1]
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        
        if start_date > end_date:
            tk.messagebox.showwarning("Uyarı", "Başlangıç tarihi bitiş tarihinden büyük olamaz")
            return

        # Çalışanın gelirini ve giderlerini hesaplar
        calisan_id = self.database.calisan_id_al(ad, soyad)

        # Gelirleri almak için sorgu
        gelir_query = """
        SELECT SUM(g.tutar) AS toplam, o.odeme
        FROM gelir g
        JOIN odeme_yontemleri o ON g.odeme_yontemi_id = o.id
        WHERE g.calisan_id = ? AND g.tarih BETWEEN ? AND ?
        GROUP BY o.odeme
        """
        self.database.cursor.execute(gelir_query, (calisan_id, start_date, end_date))
        gelirler = self.database.cursor.fetchall()

        if not gelirler:
            gelirler = [(0, "N/A")]

        gelir_mesaji = f"{ad} {soyad} adlı çalışanın geliri:\n"
        toplam_gelir = 0
        for toplam, odeme in gelirler:
            gelir_mesaji += f"{odeme}: {self.format_number(toplam)} TL\n"
            toplam_gelir += toplam

        # Giderleri almak için sorgu
        gider_query = """
        SELECT SUM(tutar) FROM gider
        WHERE calisan_id = ? AND tarih BETWEEN ? AND ?
        """
        self.database.cursor.execute(gider_query, (calisan_id, start_date, end_date))
        giderler = self.database.cursor.fetchone()[0]

        if giderler is None:
            giderler = 0

        net_kazanc = toplam_gelir - giderler

        gelir_mesaji += f"\nToplam Gelir: {self.format_number(toplam_gelir)} TL\n"
        gelir_mesaji += f"Giderler: {self.format_number(giderler)} TL\n"
        gelir_mesaji += f"Net Kazanç: {self.format_number(net_kazanc)} TL"

        # Gelir ve gider bilgilerini mesaj olarak gösterir
        self.show_info("Gelir Bilgisi", gelir_mesaji, start_date, end_date, ad, soyad)
        
        

    def maas_hesapla(self):
        # Seçilen çalışanın ad ve soyadını alır
        secilen_calisan = self.calisan_var.get()
        secilen_calisan=secilen_calisan.split()
        if not secilen_calisan:
            tk.messagebox.showwarning("Uyarı", "Lütfen bir çalışan seçin.")
            return
        if len(secilen_calisan)>2:
            ad = " ".join(secilen_calisan[:-1])
            soyad=secilen_calisan[-1]
        else:
            ad=secilen_calisan[0]
            soyad=secilen_calisan[1]
       
    
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()

        # Çalışanın toplam gelirini hesaplar
        calisan_id = self.database.calisan_id_al(ad, soyad)
        gelir_query = """
        SELECT SUM(g.tutar) AS toplam, o.odeme
        FROM gelir g
        JOIN odeme_yontemleri o ON g.odeme_yontemi_id = o.id
        WHERE g.calisan_id = ? AND g.tarih BETWEEN ? AND ?
        GROUP BY o.odeme
        """
        self.database.cursor.execute(gelir_query, (calisan_id, start_date, end_date))
        gelirler = self.database.cursor.fetchall()

        if not gelirler:
            gelirler = [(0, "N/A")]

        gelir_mesaji = f"{ad} {soyad} adlı çalışanın geliri:\n"
        toplam_gelir = 0
        for toplam, odeme in gelirler:
            gelir_mesaji += f"{odeme}: {self.format_number(toplam)} TL\n"
            toplam_gelir += toplam

        # Giderleri almak için sorgu
        gider_query = """
        SELECT SUM(tutar) FROM gider
        WHERE calisan_id = ? AND tarih BETWEEN ? AND ?
        """
        self.database.cursor.execute(gider_query, (calisan_id, start_date, end_date))
        giderler = self.database.cursor.fetchone()[0]

        if giderler is None:
            giderler = 0


        # %45 maaş hesaplama
        maas = toplam_gelir * 0.45
        self.db.maas_ekle(calisan_id,maas)


        # Maaş ve toplam gelir miktarını mesaj olarak gösterir
        maas_mesaji = f"{ad} {soyad} adlı çalışanın toplam kárı: {self.format_number(toplam_gelir)} TL\n"
        maas_mesaji += f"{ad} {soyad} adlı çalışanın maaşı: {self.format_number(maas)} TL\n"
        
        self.show_info("Maaş Hesaplama", maas_mesaji, start_date, end_date, ad, soyad, maas)

    def show_info(self, title, message, start_date, end_date, ad, soyad, maas=None):
        info_window = tk.Toplevel(self)
        info_window.title(title)
        info_window.geometry("500x400")
        info_window.configure(bg="#33373d")

        # Başlık ve tarih aralığını gösteren etiket
        header_label = tk.Label(info_window, text=f"Çalışan: {ad} {soyad}\nBaşlangıç Tarihi: {start_date}\nBitiş Tarihi: {end_date}",
                                bg="#33373d", fg="#E0E0E0", font=("Bold", 15), anchor="center", justify="center", padx=10, pady=10)
        header_label.pack(pady=15, anchor=tk.CENTER)

        # Mesajı gösteren etiket
        message_label = tk.Label(info_window, text=message,
                                bg="#33373d", fg="#FFFFFF", font=("Bold", 14), justify=tk.CENTER, anchor="center", padx=20, pady=20)
        message_label.pack(expand=True, fill=tk.BOTH, anchor=tk.CENTER)

        # Kapat butonu
        close_button = tk.Button(info_window, command=info_window.destroy,
                                image=self.f7, border=0, cursor='hand2', highlightthickness=0,  background="#33373d")
        close_button.pack(pady=10, anchor=tk.CENTER)
        
    def format_number(self, number):
        return "{:,.0f}".format(number).replace(',', '.')