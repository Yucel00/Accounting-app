from datetime import date
import tkinter as tk
from tkinter import ttk
from util import *
from mail_service import *
from grafik import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

BUGUN = date.today().strftime("%d-%m-%Y")

class RaporPenceresi:
    def __init__(self, parent, bas_date, son_date, gelir_toplam, gider_toplam, kar, f5, f6,f16, send_email_in_thread, subject, db):
        self.parent = parent
        self.bas_date = bas_date
        self.son_date = son_date
        self.gelir_toplam = gelir_toplam
        self.gider_toplam = gider_toplam
        self.kar = kar
        self.f5 = f5
        self.f6 = f6
        self.f16=f16
        self.db = db
        self.bg_color = "#33373d"
        self.header_bg_color = "#1B4242"
        self.header_fg_color = "#E0E0E0"
        self.balslık_color ="black"
        self.row_bg_color = "#505050"
        self.row_fg_color = "#E0E0E0"
        self.font = ("Bold", 15)
        self.send_email_in_thread = send_email_in_thread
        self.subject = subject

        self.create_rapor_penceresi()

    def format_number(self, number):
        """ Sayıları binlik ayırıcı nokta ile formatlar ve sonuna TL ekler """
        if isinstance(number, (int, float)):  # Sayısal değerler için formatlama
            return "{:,.0f}".format(number).replace(',', '.') + " TL"
        elif number == 0:  # 0 değerini işleme
            return "0 TL"
        else:  # Diğer değerler için döndürme
            return str(number)  # String olarak döndür

    def create_rapor_penceresi(self):
        rapor_penceresi = tk.Toplevel(self.parent)
        rapor_penceresi.title("Rapor Özeti")
        rapor_penceresi.configure(bg=self.bg_color)

        # Pencere boyutunu ayarla
        window_height = 850
        window_width = 1150
        x_cordinate = int((rapor_penceresi.winfo_screenwidth() / 2) - (window_width / 2))
        y_cordinate = int((rapor_penceresi.winfo_screenheight() / 2) - (window_height / 2))
        rapor_penceresi.geometry(f'{window_width}x{window_height}+{x_cordinate}+{y_cordinate}')

        # Başlık
        rapor_label = tk.Label(rapor_penceresi, text=f"Rapor Türü: {self.subject}", bg=self.bg_color, fg=self.header_fg_color, font=self.font)
        rapor_label.pack(pady=10)

        tarih_araligi_label = tk.Label(rapor_penceresi, text=f"Tarih Aralığı: {self.bas_date} - {self.son_date}", bg=self.bg_color, fg=self.header_fg_color, font=self.font)
        tarih_araligi_label.pack(pady=10)

        # Treeview stilini özelleştirme
        style = ttk.Style()
        style.theme_use("default")

        # Başlık (header) için stil
        style.configure("Custom.Treeview.Heading", 
                        background=self.header_bg_color, 
                        foreground=self.header_fg_color, 
                        font=self.font)

        # Satırlar (rows) için stil
        style.configure("Custom.Treeview", 
                        background=self.row_bg_color, 
                        foreground=self.row_fg_color, 
                        rowheight=30, 
                        fieldbackground=self.row_bg_color,
                        font=("Arial", 12))

        # Hover efekti için stil
        style.map("Custom.Treeview.Heading",
                background=[('active', '#536493')])  # başlık araplan

        # Tabloyu içeren bir çerçeve oluşturma
        table_frame = tk.Frame(rapor_penceresi, bg=self.bg_color)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Tablo oluşturma
        columns = ["Çalışan", "Gelir (IBAN)", "Gelir (Nakit)", "Gelir (Kredi Kartı)", "Gider", "Toplam Kazanç", "Kâr"]
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")
        tree.pack(fill=tk.BOTH, expand=True)

        # Sütun başlıklarını ayarla
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=140)

        # Verileri ekleme
        data = self.db.calisan_bazli_rapor(self.bas_date, self.son_date)
        row_colors = [self.row_bg_color, "#404040"]  # Daha açık bir siyah için #404040

        email_body = f"""
        <html>
        <body>
            <h2 style="color: {self.balslık_color};">Rapor Türü: {self.subject}</h2>
            <p><strong>Tarih Aralığı:</strong> {self.bas_date} - {self.son_date}</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%; background-color: {self.bg_color};">
                <thead style="background-color: {self.header_bg_color}; color: {self.header_fg_color};">
                    <tr>
                        <th>Çalışan</th>
                        <th>Gelir (IBAN)</th>
                        <th>Gelir (Nakit)</th>
                        <th>Gelir (Kredi Kartı)</th>
                        <th>Gider</th>
                        <th>Toplam Kazanç</th>
                        <th>Kâr</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        pdf_data = [["Çalışan", "Gelir (IBAN)", "Gelir (Nakit)", "Gelir (Kredi Kartı)", "Gider", "Toplam Kazanç", "Kâr"]]

        for index, row_data in enumerate(data):
            # None değerlerini 0 ile değiştir
            row_data = [0 if cell is None else cell for cell in row_data]
            total_income = sum(row_data[1:4])
            gider = row_data[4]
            profit = total_income - gider
            row_data = list(row_data) + [total_income, profit]
            formatted_row = [self.format_number(cell) for cell in row_data]
            tree.insert("", tk.END, values=formatted_row)
            
            # Satır rengini belirleme
            row_color = row_colors[index % 2]
            
            email_body += f"""
            <tr style="background-color: {row_color}; color: {self.row_fg_color};">
                <td>{formatted_row[0]}</td>
                <td>{formatted_row[1]}</td>
                <td>{formatted_row[2]}</td>
                <td>{formatted_row[3]}</td>
                <td>{formatted_row[4]}</td>
                <td>{formatted_row[5]}</td>
                <td>{formatted_row[6]}</td>
            </tr>
            """
            
            pdf_data.append(formatted_row)

        email_body += f"""
                </tbody>
            </table>
            <p><strong>Toplam Gelir:</strong> {self.format_number(self.gelir_toplam)}</p>
            <p><strong>Toplam Gider:</strong> {self.format_number(self.gider_toplam)}</p>
            <p><strong>Kâr:</strong> {self.format_number(self.kar)}</p>
        </body>
        </html>
        """

        # Toplam gelir, gider ve kar bilgilerini yatay olarak yerleştirme
        toplam_frame = tk.Frame(rapor_penceresi, bg=self.bg_color)
        toplam_frame.pack(pady=10)

        toplam_gelir_label = tk.Label(toplam_frame, text=f"Toplam Gelir: {self.format_number(self.gelir_toplam)}", bg=self.bg_color, fg=self.header_fg_color, font=self.font)
        toplam_gelir_label.pack(side=tk.LEFT, padx=20)

        toplam_gider_label = tk.Label(toplam_frame, text=f"Toplam Gider: {self.format_number(self.gider_toplam)}", bg=self.bg_color, fg=self.header_fg_color, font=self.font)
        toplam_gider_label.pack(side=tk.LEFT, padx=20)

        kar_label = tk.Label(toplam_frame, text=f"Kâr: {self.format_number(self.kar)}", bg=self.bg_color, fg=self.header_fg_color, font=self.font)
        kar_label.pack(side=tk.LEFT, padx=20)

        # Grafik oluşturma
        grafik(rapor_penceresi, self.gelir_toplam, self.gider_toplam)

        # Butonlar için alt kısımda ayrı bir çerçeve oluşturma
        button_frame = tk.Frame(rapor_penceresi, bg=self.bg_color)
        button_frame.pack(side=tk.BOTTOM, pady=20)

        # Kapat butonu
        close_button = tk.Button(button_frame,image=self.f6, border=0, cursor='hand2', highlightthickness=0, background=self.bg_color, command=rapor_penceresi.destroy)
        close_button.pack(side=tk.RIGHT, padx=10)


        # E-posta Gönder butonu
        email_butonu = tk.Button(button_frame, image=self.f5, border=0, cursor='hand2', highlightthickness=0, background=self.bg_color,
                            command=lambda: self.send_email_in_thread(RECIPIENT, self.subject, email_body))
        email_butonu.pack(side=tk.RIGHT, padx=20)

        # PDF olarak kaydet butonu
        
        save_pdf_button = tk.Button(button_frame, image=self.f16, border=0, cursor='hand2', highlightthickness=0, background=self.bg_color, command=lambda: self.save_as_pdf(pdf_data))
        save_pdf_button.pack(side=tk.LEFT, padx=10)

    def save_as_pdf(self, data):
        # PDF dosyasının adını ve kaydedileceği dizini belirleyin
        directory = os.path.expanduser("~/Desktop/PDF YEDEK")  # Kullanıcının masaüstüne kaydeder
        
        # Klasörün mevcut olup olmadığını kontrol et ve gerekirse oluştur
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        pdf_filename = os.path.join(directory, f"{self.subject}({BUGUN}).pdf")

        # PDF dosyasını oluşturma
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)
        elements = []

        # Arial yazı tipini kaydetme ve kullanma
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

        # Başlıkları ekleme
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontName = 'Arial'
        title_style.fontSize = 18

        # Başlıklar
        title = Paragraph(f"Rapor Türü: {self.subject}", title_style)
        date_range = Paragraph(f"Tarih Aralığı: {self.bas_date} - {self.son_date}", title_style)
        
        # Başlıkları PDF'e ekleme
        elements.append(title)
        elements.append(date_range)
        elements.append(Paragraph("<br/>", styles['Normal']))  # Boşluk ekleme

        # Tabloyu oluşturma
        table = Table(data)

        # Tablo stilini ayarlama
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.header_bg_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(self.header_fg_color)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(self.row_bg_color)),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(self.row_fg_color)),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),  # Arial fontunu kullan
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ])
        table.setStyle(style)

        # Tabloyu PDF'e ekleme
        elements.append(table)
        elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Tablo ile toplam bilgileri arasına boşluk ekleme

        # Toplam gelir, gider ve kar bilgilerini ekleme
        summary_style = styles['Normal']
        summary_style.fontName = 'Arial'
        summary_style.fontSize = 14

        summary_data = [
            ["Toplam Gelir:", self.format_number(self.gelir_toplam)],
            ["Toplam Gider:", self.format_number(self.gider_toplam)],
            ["Kâr:", self.format_number(self.kar)]
        ]

        # Toplam verileri hizalamak için tablo oluşturma
        summary_table = Table(summary_data, colWidths=[150, 150])

        # Toplam tablo stilini ayarlama
        summary_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.header_bg_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(self.header_fg_color)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(self.bg_color)),  # Arka plan rengini ayarla
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#FFFFFF"))  # Metin rengini beyaz yap
        ])

        summary_table.setStyle(summary_style)

        # Toplam verileri PDF'e ekleme
        elements.append(summary_table)

        try:
            pdf.build(elements)
            messagebox.showinfo("Success",f"PDF dosyası başarıyla '{pdf_filename}' olarak kaydedildi.")
            
        except Exception as e:
            messagebox.showerror("Eror",f"PDF dosyası kaydedilirken bir hata oluştu: {str(e)}")
        







