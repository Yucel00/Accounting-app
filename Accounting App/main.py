import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from tkcalendar import DateEntry
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from tkinter import messagebox
import locale
import babel.numbers
import threading
from mail_service import *
from database import *
from util import *
from grafik import *
from rapor_windows import *
from gelir_goster import GelirGosterApp
from gelir_goster import *

locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
BUGUN = date.today()
gun=BUGUN.strftime("%A")



ODEME_YONTEMI =["Nakit", "IBAN", "Kredi Kartı"]



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Muhasebe Uygulaması")
        window_height = 680
        window_width = 1300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.geometry(f'{window_width}x{window_height}+{x_cordinate}+{y_cordinate}')
        self.configure(bg=bg_color)
        self.resizable(0, 0)
        self.db=Database()
        
        self.create_widgets()
        
        
    



    def create_widgets(self):
        self.kisiler =self.db.liste_olustur()
        self.db.odeme_yontemleri(ODEME_YONTEMI)
        
        
        # Başlık
        self.f1 = ImageTk.PhotoImage(Image.open("images/Frame2.png"))
        self.f2 = ImageTk.PhotoImage(Image.open("images/Frame3.png"))
        self.f3 = ImageTk.PhotoImage(Image.open("images/Frame4.png"))
        self.f4 = ImageTk.PhotoImage(Image.open("images/Frame5.png"))
        self.f5 = ImageTk.PhotoImage(Image.open("images/Frame6.png"))
        self.f6 = ImageTk.PhotoImage(Image.open("images/Frame7.png"))
        self.f7 = ImageTk.PhotoImage(Image.open("images/Frame8.png"))
        self.f8 = ImageTk.PhotoImage(Image.open("images/Frame9.png"))
        self.f9 = ImageTk.PhotoImage(Image.open("images/Frame10.png"))
        self.f10 = ImageTk.PhotoImage(Image.open("images/Frame11.png"))
        self.f12 = ImageTk.PhotoImage(Image.open("images/Frame13.png"))
        self.f16 = ImageTk.PhotoImage(Image.open("images/Frame16.png"))
        self.f17 = ImageTk.PhotoImage(Image.open("images/Frame17.png"))

        
        self.main_label = tk.Label(self, text="Muhasebe Uygulaması", bg=title_bg, fg=title_fg, font=("Bold", 24), pady=10)
        self.main_label.pack(fill=tk.X)
        main_frame = tk.Frame(self, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sol çerçeve
        left_frame = tk.Frame(main_frame, bg=bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sağ çerçeve 
        self.right_frame = tk.Frame(main_frame, bg=bg_color)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        # Listbox ekle
        self.listbox_1 = tk.Listbox(self.right_frame, width=100, height=8, bg=entry_bg, fg=entry_fg,
                                    selectbackground=button_bg, selectforeground=button_fg, font=("Bold", 13))
        self.listbox_1.pack(pady=10)
        
        
        #yapılanı geri al
        geri_al_button = tk.Button(self.right_frame, image=self.f8, border=0, cursor='hand2', highlightthickness=0, background=bg_color,command=lambda:self.db.geri_al(self.listbox_1))
        geri_al_button.pack(pady=10)

        self.rightmidframe=tk.Frame(self.right_frame,bg=bg_color)
        self.rightmidframe.pack(pady=10)
        # Kişi seçimi için Frame
        person_frame = tk.Frame(left_frame, bg=bg_color)
        person_frame.pack(pady=10)

        kisi_label = tk.Label(person_frame, text="Kişi Seç:", bg=bg_color, fg=label_fg, font=font)
        kisi_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        #liste oluşturma
        self.selected_person = tk.StringVar()
        self.selected_person.set(self.kisiler[0] if self.kisiler else "")  # Varsayılan olarak ilk kişiyi seç
        
        #drodown menü oluşturma
        self.optionmenu_person = tk.OptionMenu(person_frame, self.selected_person, *self.kisiler)
        self.optionmenu_person.config(bg=entry_bg, fg=entry_fg, font=("Arial", 12), width=15, borderwidth=2, relief="flat")
        self.optionmenu_person.grid(row=0, column=1, padx=10, pady=10)
        
        # Açılan menünün arka plan rengini değiştirme
        menu = self.optionmenu_person.nametowidget(self.optionmenu_person.menuname)  # Menü widget'ını al
        menu.config(bg=entry_bg, fg=entry_fg)  # Menü arka plan ve yazı rengini ayarla

        # Kişi Ekle ve Kişi Kaldır butonları
        kisi_ekle_button = tk.Button(person_frame, image=self.f9, border=0, cursor='hand2', highlightthickness=0, background=bg_color,command=self.open_kisi_ekle_pencere)
        kisi_ekle_button.grid(row=0, column=2, padx=10, pady=10)

        kisi_kaldir_button = tk.Button(person_frame, image=self.f7, border=0, cursor='hand2', highlightthickness=0, background=bg_color, command=self.open_kisi_cikar_pencere)
        kisi_kaldir_button.grid(row=0, column=3, padx=10, pady=10)

        # Gelir ve Gider entry'leri için Frame ve widgetlar
        entry_frame = tk.Frame(left_frame, bg=bg_color)
        entry_frame.pack(pady=20)

        gelir_label = tk.Label(entry_frame, text="Gelir:", bg=bg_color, fg=label_fg, font=font)
        gelir_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.gelir_entry = tk.Entry(entry_frame, bg=entry_bg, fg=entry_fg, width=12, font=font, borderwidth=2, relief="groove")
        self.gelir_entry.grid(row=0, column=1, padx=10, pady=10)

        self.gimage = ImageTk.PhotoImage(Image.open("images/button.png"))
        gelir_button = tk.Button(entry_frame, image=self.gimage, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                command=lambda: self.gelir_gider(1))
        gelir_button.grid(row=0, column=3)

        gider_label = tk.Label(entry_frame, text="Gider:", bg=bg_color, fg=label_fg, font=font)
        gider_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.gider_entry = tk.Entry(entry_frame, bg=entry_bg, fg=entry_fg, width=12, font=font)
        self.gider_entry.grid(row=1, column=1, padx=10, pady=10)

        gider_button = tk.Button(entry_frame, image=self.gimage, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                command=lambda: self.gelir_gider(2))
        gider_button.grid(row=1, column=3, padx=10, pady=10)

        # ödeme yöntemi için dropdown menüler
        self.selected_var_gelir = tk.StringVar()
        self.selected_var_gelir.set(ODEME_YONTEMI[0])

        self.selected_var_gider = tk.StringVar()
        self.selected_var_gider.set(ODEME_YONTEMI[0])

        # Gelir dropdown menü oluşturma
        dropdown_menu_gelir = tk.OptionMenu(entry_frame, self.selected_var_gelir, *ODEME_YONTEMI)
        dropdown_menu_gelir.config(bg=entry_bg, fg=entry_fg, font=("Arial", 12), width=10, borderwidth=2, relief="flat")
        dropdown_menu_gelir.grid(row=0, column=2, padx=10, pady=10)
        
        # Açılan menünün arka plan rengini değiştirme
        menu_gelir = dropdown_menu_gelir['menu']  # Menü widget'ını al
        menu_gelir.config(bg=entry_bg, fg=entry_fg)  # Menü arka plan ve yazı rengini ayarla

        # Gider dropdown menü oluşturma
        dropdown_menu_gider = tk.OptionMenu(entry_frame, self.selected_var_gider, *ODEME_YONTEMI)
        dropdown_menu_gider.config(bg=entry_bg, fg=entry_fg, font=("Arial", 12), width=10, borderwidth=2, relief="flat")
        dropdown_menu_gider.grid(row=1, column=2, padx=10, pady=10)
        
        # Açılan menünün arka plan rengini değiştirme
        menu_gider = dropdown_menu_gider['menu']  # Menü widget'ını al
        menu_gider.config(bg=entry_bg, fg=entry_fg)  # Menü arka plan ve yazı rengini ayarla

        # Tarih frame ve labelları
        date_frame = tk.Frame(left_frame, bg=bg_color)
        date_frame.pack(pady=20)

        start_date_label = tk.Label(date_frame, text="Başlangıç Tarihi:", bg=bg_color, fg=label_fg, font=font)
        start_date_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.date1 = DateEntry(date_frame, locale="tr_TR", width=15, font=font)
        self.date1.grid(row=0, column=1, padx=10, pady=10)

        end_date_label = tk.Label(date_frame, text="Bitiş Tarihi:", bg=bg_color, fg=label_fg, font=font)
        end_date_label.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)

        self.date2 = DateEntry(date_frame, locale="tr_TR", width=15, font=font)
        self.date2.grid(row=0, column=3, padx=10, pady=10)

        aralik_button = tk.Button(date_frame, image=self.f1, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                command=lambda: self.aralık_rapor("aralık"))
        aralik_button.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        # Rapor Butonları
        rapor_frame = tk.Frame(left_frame, bg=bg_color)
        rapor_frame.pack(pady=20)

        haftalik_button = tk.Button(rapor_frame, image=self.f2, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                    command=lambda: self.aralık_rapor("haftalıkButton"))
        haftalik_button.grid(row=0, column=0, padx=15, pady=10)

        aylik_button = tk.Button(rapor_frame, image=self.f3, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                command=lambda: self.aralık_rapor("aylıkButton"))
        aylik_button.grid(row=0, column=1, padx=15, pady=10)

        yıllık_button = tk.Button(rapor_frame, image=self.f4, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                command=lambda: self.aralık_rapor("yıllıkButton"))
        yıllık_button.grid(row=0, column=2, padx=15, pady=10)
        
        self.gelir_goster_button = tk.Button(rapor_frame, image=self.f12, border=0, cursor='hand2', highlightthickness=0, background=bg_color, command=self.gelir_goster)
        self.gelir_goster_button.grid(row=1, column=1, padx=15, pady=10)

        # Pasta grafiğini ekleyin
        self.gunlukgelir,self.gunlukgider=self.db.aralik_al(BUGUN,BUGUN)#gunluk gelir ve gunluk gideri almak icin database py de olusturdugumuz aralik al fonksiyonumuz icine tarih parametrelerimizi bugun olarak girdik
        grafik(self.rightmidframe,self.gunlukgelir,self.gunlukgider)#grafik sayfamida olusturdugumuz onksiyona ihtiyaci olan frame gelir ve gider parametrelerini gonderdik

         
    def gelir_gider(self, buton_no):
        secilen_kisi = self.selected_person.get()
        
        # Kullanıcının bir kişi seçip seçmediğini kontrol et
        if secilen_kisi:
            # Seçilen kişinin adını ve soyadını ayır
            secilen_kisi_format = secilen_kisi.split()
            if len(secilen_kisi_format)>2:
                secilen_kisi_ad = " ".join(secilen_kisi_format[:-1])
                secilen_kisi_soyad = secilen_kisi_format[-1]
            else:
                secilen_kisi_ad = secilen_kisi_format[0]
                
                secilen_kisi_soyad = secilen_kisi_format[-1]

           

            # Çalışan ID'sini al
            secilen_kisi_id = self.db.calisan_id_al(secilen_kisi_ad, secilen_kisi_soyad)
            

            # Eğer çalışan bulunamazsa hata göster ve fonksiyonu sonlandır
            if secilen_kisi_id is None:
                messagebox.showerror("Hata", "Çalışan bulunamadı!")
                return

            # Ödeme yöntemlerini al
            odeme_yontemi_gelir = self.selected_var_gelir.get()
            odeme_yontemi_gider = self.selected_var_gider.get()
            gelir_odeme_id = self.db.odeme_id_al(odeme_yontemi_gelir)
            gider_odeme_id = self.db.odeme_id_al(odeme_yontemi_gider)
        else:
            messagebox.showerror("Hata", "Eleman Yok!")
            return

        try:
            if buton_no == 1:  # Gelir butonuna basıldığında
                a = self.gelir_entry.get()
                a = float(a)
                if a < 0:
                    self.gelir_entry.delete(0, tk.END)
                    messagebox.showerror("Hata", "Negatif Gelir Girilmez!")
                    return

                # Aynı tarih, çalışan ve ödeme yöntemi ile bir gelir var mı kontrol et
                self.db.cursor.execute("""
                    SELECT id, tutar FROM gelir
                    WHERE tarih = ? AND calisan_id = ? AND odeme_yontemi_id = ?
                """, (str(BUGUN), secilen_kisi_id, gelir_odeme_id))
                mevcut_gelir = self.db.cursor.fetchone()

                if mevcut_gelir:  # Mevcut bir gelir varsa güncelle
                    yeni_tutar = mevcut_gelir[1] + a
                    self.db.cursor.execute("""
                        UPDATE gelir
                        SET tutar = ?
                        WHERE id = ?
                    """, (yeni_tutar, mevcut_gelir[0]))
                else:  # Yoksa yeni bir satır ekle
                    self.db.cursor.execute("""
                        INSERT INTO gelir (tarih, gun, tutar, calisan_id, odeme_yontemi_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(BUGUN), gun, a, secilen_kisi_id, gelir_odeme_id))

                self.db.conn.commit()

                # Eski grafiği kaldır
                for widget in self.rightmidframe.winfo_children():
                    widget.destroy()

                # Yeni grafik oluştur
                self.gunlukgelir, self.gunlukgider = self.db.aralik_al(BUGUN, BUGUN)
                grafik(self.rightmidframe, self.gunlukgelir, self.gunlukgider)

                formatted_amount = self.format_number(a)

                if self.listbox_1.size() == 10:
                    self.listbox_1.delete(tk.END)
                self.listbox_1.insert(0, f"{BUGUN} {secilen_kisi} {odeme_yontemi_gelir} ile {formatted_amount} Gelir Eklendi")
                self.gelir_entry.delete(0, tk.END)

            else:  # Gider butonuna basıldığında
                b = self.gider_entry.get()
                b = float(b)
                if b < 0:
                    self.gider_entry.delete(0, tk.END)
                    messagebox.showerror("Hata", "Negatif Gider Girilmez!")
                    return

                # Aynı tarih, çalışan ve ödeme yöntemi ile bir gider var mı kontrol et
                self.db.cursor.execute("""
                    SELECT id, tutar FROM gider
                    WHERE tarih = ? AND calisan_id = ? AND odeme_yontemi_id = ?
                """, (str(BUGUN), secilen_kisi_id, gider_odeme_id))
                mevcut_gider = self.db.cursor.fetchone()

                if mevcut_gider:  # Mevcut bir gider varsa güncelle
                    yeni_tutar = mevcut_gider[1] + b
                    self.db.cursor.execute("""
                        UPDATE gider
                        SET tutar = ?
                        WHERE id = ?
                    """, (yeni_tutar, mevcut_gider[0]))
                else:  # Yoksa yeni bir satır ekle
                    self.db.cursor.execute("""
                        INSERT INTO gider (tarih, gun, tutar, calisan_id, odeme_yontemi_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(BUGUN), gun, b, secilen_kisi_id, gider_odeme_id))

                self.db.conn.commit()

                # Eski grafiği kaldır
                for widget in self.rightmidframe.winfo_children():
                    widget.destroy()

                # Yeni grafik oluştur
                self.gunlukgelir, self.gunlukgider = self.db.aralik_al(BUGUN, BUGUN)
                grafik(self.rightmidframe, self.gunlukgelir, self.gunlukgider)

                formatted_amount = self.format_number(b)

                if self.listbox_1.size() == 10:
                    self.listbox_1.delete(tk.END)
                self.listbox_1.insert(0, f"{BUGUN} {secilen_kisi} {odeme_yontemi_gider} ile {formatted_amount} Gider Eklendi")
                self.gider_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Hata", "Sadece rakam girilebilir!")
            self.gelir_entry.delete(0, tk.END)
            self.gider_entry.delete(0, tk.END)
            return  # Hata durumunda işlemi durdurur




    def format_number(self, number):
        return "{:,.0f}".format(number).replace(',', '.') + " TL"
  

    def aralık_rapor(self, rapor_tipi):
        if rapor_tipi == "aralık":
            bas_date = self.date1.get_date()
            son_date = self.date2.get_date()
            gelir_toplam, gider_toplam = self.db.aralik_al(bas_date,son_date)
            if bas_date>son_date:
                tk.messagebox.showwarning("Uyarı", "Başlangıç tarihi bitiş tarihinden büyük olamaz")
                return
            kar=self.db.kar_al(bas_date,son_date)
            SUBJECT=f"Aralık Rapor"    

        elif rapor_tipi == "haftalıkButton":
            bas_date = BUGUN - timedelta(days=7)
            son_date = BUGUN
            gelir_toplam, gider_toplam = self.db.aralik_al(bas_date,son_date)
            kar=self.db.kar_al(bas_date,son_date)

            SUBJECT=f"Haftalık Rapor"

        elif rapor_tipi == "aylıkButton":
            bas_date = BUGUN - relativedelta(months=1)
            son_date = BUGUN
            gelir_toplam, gider_toplam = self.db.aralik_al(bas_date,son_date)
            kar=self.db.kar_al(bas_date,son_date)

            SUBJECT=f"Aylık Rapor"
            
        elif rapor_tipi == "yıllıkButton":
            bas_date = BUGUN - relativedelta(years=1)
            son_date = BUGUN
            gelir_toplam, gider_toplam = self.db.aralik_al(bas_date,son_date)
            kar=self.db.kar_al(bas_date,son_date)

            SUBJECT=f"Yıllık Rapor"
            
        # rapor pencerelerini olustur
        RaporPenceresi(self, bas_date, son_date, gelir_toplam, gider_toplam, kar, self.f5, self.f6,self.f16, send_email_in_thread, SUBJECT, self.db)
#-------------------------------------------------------------------------------------------------------------------------------------------------------#
    #kişi ekle fonksiyonu
    def open_kisi_ekle_pencere(self):
        # Yeni pencere aç
        kisi_pencere = tk.Toplevel(self)
        kisi_pencere.title("Kişi Ekle")
        kisi_pencere.geometry("500x300")
        kisi_pencere.configure(bg=bg_color)
        kisi_pencere.resizable(0, 0)

        # Pencerenin boyutlarını al
        window_width = 500
        window_height = 300
        screen_width = kisi_pencere.winfo_screenwidth()
        screen_height = kisi_pencere.winfo_screenheight()

        # Pencerenin ekranın ortasında olmasını sağla
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        kisi_pencere.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # İçerik için bir çerçeve oluştur ve ortala
        frame = tk.Frame(kisi_pencere, bg=bg_color)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Frame içinde grid düzenini ayarla
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # İsim giriş alanı
        isim_label = tk.Label(frame, text="İsim:", bg=bg_color, fg=label_fg, font=font)
        isim_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.isim_entry = tk.Entry(frame, bg=entry_bg, fg=entry_fg, width=20, font=font)
        self.isim_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
       
        
        # Soyisim giriş alanı
        soyisim_label = tk.Label(frame, text="Soyisim:", bg=bg_color, fg=label_fg, font=font)
        soyisim_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.soyisim_entry = tk.Entry(frame, bg=entry_bg, fg=entry_fg, width=20, font=font)
        self.soyisim_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
       

        # Kişi ekleme butonu, Entry alanlarıyla aynı hizada olacak
        kisi_ekle_button = tk.Button(frame, image=self.gimage, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                    command=lambda: self.kisi_ekle( kisi_pencere))
        kisi_ekle_button.grid(row=2, column=1, padx=10, pady=20, sticky="w")

    #ekle butonunda kisi ad soyadini alip database ve dropdowna ekleyen fonksiyon 
    def kisi_ekle(self,pencere):
        isim=self.isim_entry.get().strip()
        soyisim=self.soyisim_entry.get().strip()
        if len(isim)==0 or len(soyisim)==0:
            messagebox.showerror("Hata", "Isim Veya Soyisim Boş Olamaz")
            return
        else:
            self.db.calisan_ekle(isim, soyisim)
        
            self.db.conn.commit()
            
            # Kisiler listesini güncelle
            self.kisiler = self.db.liste_olustur()

            # Dropdown menüsünü güncelle
            self.dropdown_menu_gunceleme()
            
            # Varsayılan olarak yeni eklenen kişiyi seç
            self.selected_person.set(f"{isim.title()} {soyisim.title()}")

            # Pencereyi kapat
            pencere.destroy()
            
    

   
    #kişi çıkarmak için fonksiyon            
    def open_kisi_cikar_pencere(self):
        # Yeni pencere aç
        kisi_cikar_pencere = tk.Toplevel(self)
        kisi_cikar_pencere.title("Kişi Çıkar")
        kisi_cikar_pencere.geometry("500x300")
        kisi_cikar_pencere.configure(bg=bg_color)
        kisi_cikar_pencere.resizable(0, 0)

        # Pencerenin boyutlarını al
        window_width = 500
        window_height = 300
        screen_width = kisi_cikar_pencere.winfo_screenwidth()
        screen_height = kisi_cikar_pencere.winfo_screenheight()

        # Pencerenin ekranın ortasında olmasını sağla
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        kisi_cikar_pencere.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # İçerik için bir çerçeve oluştur ve ortala
        frame = tk.Frame(kisi_cikar_pencere, bg=bg_color)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Frame içinde grid düzenini ayarla
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Kişi seçimi için label ve dropdown menu
        kisi_label = tk.Label(frame, text="Kişi Seç:", bg=bg_color, fg=label_fg, font=font)
        kisi_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.selected_person_to_remove = tk.StringVar()
        self.selected_person_to_remove.set(self.kisiler[0] if self.kisiler else "")  # Varsayılan olarak ilk kişiyi seçer
        
        self.dropdown_menu_kisi_cikar = tk.OptionMenu(frame, self.selected_person_to_remove, *self.kisiler)
        self.dropdown_menu_kisi_cikar.config(bg=entry_bg, fg=entry_fg, font=("Arial", 12), width=15, borderwidth=1, relief="groove")
        self.dropdown_menu_kisi_cikar.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Kişi çıkarma butonu
        kisi_cikar_button = tk.Button(frame, image=self.f10, border=0, cursor='hand2', highlightthickness=0, background=bg_color,
                                    command=lambda: self.kisi_çıkarma_onay(kisi_cikar_pencere))
        kisi_cikar_button.grid(row=1, column=1, padx=10, pady=20, sticky="w")


    def kisi_çıkarma_onay(self, kisi_cikar_pencere):
        # Onaylama penceresi
        result = messagebox.askyesno("Onay", f"{self.selected_person_to_remove.get()} kişisini çıkarmak istediğinize emin misiniz?")
        if result:
            self.kisi_çıkar()
            kisi_cikar_pencere.destroy()

    def kisi_çıkar(self):
        # Seçilen kişiyi listeden kaldır
        try:
            selected_person = self.selected_person_to_remove.get()
            selected_person=selected_person.split(" ")
            if len(selected_person)>2:
                ad = " ".join(selected_person[:-1]).title()
                soyad=selected_person[-1].title()
            else:
                ad=selected_person[0].title()
                soyad=selected_person[1].title()
            self.db.calisan_cikar(ad,soyad)
            self.kisiler = self.db.liste_olustur()
            self.db.conn.commit()
            self.dropdown_menu_gunceleme()
            name=self.kisiler[0]
            print(name)
            if name=="":
                self.selected_person.set(f" ")
            else:
                name=name.split(" ")
                ad=name[0]
                soyad=name[1]
                self.selected_person.set(f"{ad.title()} {soyad.title()}")

        except:
            messagebox.showerror("Hata", "Eleman Yok.")
            
            
    def dropdown_menu_gunceleme(self):
    # Mevcut OptionMenu'yu güncelle
        menu = self.optionmenu_person['menu']
        menu.delete(0, 'end')  # Mevcut tüm seçenekleri sil

        # Yeni seçenekleri ekle
        for kisi in self.kisiler:
            menu.add_command(label=kisi, command=lambda value=kisi: self.selected_person.set(value))
    
    
    def gelir_goster(self):
        # GelirGosterApp penceresini açar
        gelir_goster_penceresi = GelirGosterApp(self.db)
        gelir_goster_penceresi.grab_set()  # Ana pencerenin üzerini kapatır
    
            

if __name__ == "__main__":
    app = App()
    app.mainloop()