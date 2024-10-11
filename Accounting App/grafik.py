import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from util import *

def grafik(frame, gelir, gider):
    # Verilerin türünü kontrol et
    if isinstance(gelir, (int, float)):
        gelir_val = float(gelir)
    else:
        gelir_val = 0  # Varsayılan değer

    if isinstance(gider, (int, float)):
        gider_val = float(gider)
    else:
        gider_val = 0  # Varsayılan değer

    figure, ax = plt.subplots(figsize=(7, 2.5))  # Figür boyutunu ayarlayın (Genişlik x Yükseklikax
    
    labels = ['Gelir', 'Gider']
    sizes = [gelir_val, gider_val]  # Başlangıçta 0 değerler

    # Arka plan rengini uygulamanın arka plan rengine ayarlayın
    ax.clear()
    figure.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    if any(size < 0 for size in sizes) or all(size == 0 for size in sizes):
        sizes = [1, 1]  # Varsayılan değerler kullanarak grafiği oluştur

    # Renkleri güncelle
    colors = ['#28a745', '#dc3545']  # Yeşil (Gelir) ve Kırmızı (Gider)

    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
                                      wedgeprops=dict(width=0.3, edgecolor='black'))

    ax.set_title("Gelir ve Gider Dağılımı", color=label_fg)

    # Yazı renklerini beyaz yap
    for text in texts:
        text.set_color('white')
    for autotext in autotexts:
        autotext.set_color('white')

    # Pasta grafiğini Tkinter'e entegre etme
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas_widget = canvas.get_tk_widget()
    # Tkinter widget boyutunu ayarlayın
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=10, pady=10)
    canvas.draw()



       