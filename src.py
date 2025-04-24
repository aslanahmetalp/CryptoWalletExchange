import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global dictionaries
coin_dict = {}            # display_name -> coin_id
coin_logo_urls = {}       # display_name -> logo URL
logo_images = {}          # display_name -> PhotoImage cache

# Functions

def load_coins():
    """
    Fetch top 100 coins, populate combobox and store logo URLs.
    """
    global coin_dict, coin_logo_urls
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc",
              "per_page": 100, "page": 1, "sparkline": False}
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        coins = resp.json()
    except Exception as e:
        messagebox.showerror("Hata", f"Coin verileri alınamadı:\n{e}")
        return

    coin_dict.clear()
    coin_logo_urls.clear()
    names = []
    for coin in coins:
        name = f"{coin['name']} ({coin['symbol'].upper()})"
        coin_dict[name] = coin['id']
        coin_logo_urls[name] = coin.get('image')
        names.append(name)

    coin_combobox['values'] = names
    if names:
        coin_combobox.current(0)
        update_logo(names[0])


def update_logo(selected):
    """
    Load and display logo for selected coin.
    """
    url = coin_logo_urls.get(selected)
    if not url:
        logo_label.config(image='')
        return
    try:
        if selected not in logo_images:
            img_data = requests.get(url).content
            img = Image.open(BytesIO(img_data)).resize((64, 64), Image.ANTIALIAS)
            logo_images[selected] = ImageTk.PhotoImage(img)
        logo_label.config(image=logo_images[selected])
    except Exception:
        logo_label.config(image='')


def convert_coin():
    """
    Perform conversion and show results.
    """
    sel = coin_combobox.get()
    if not sel:
        messagebox.showerror("Hata", "Lütfen bir coin seçiniz!")
        return
    try:
        amt = float(amount_entry.get().strip())
    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir miktar giriniz!")
        return

    currencies = []
    if var_usd.get(): currencies.append('usd')
    if var_eur.get(): currencies.append('eur')
    if var_try.get(): currencies.append('try')
    if not currencies:
        messagebox.showerror("Hata", "Lütfen en az bir para birimi seçiniz!")
        return

    cid = coin_dict.get(sel)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies={','.join(currencies)}"
    try:
        data = requests.get(url).json()
        prices = data.get(cid, {})
    except Exception as e:
        messagebox.showerror("Hata", f"Fiyat alınamadı:\n{e}")
        return

    lines = [f"{amt} {sel.split()[0]}:"]
    for curr in currencies:
        price = prices.get(curr)
        if price is not None:
            conv = price * amt
            label = 'TL' if curr == 'try' else curr.upper()
            lines.append(f"{label}: {conv:,.2f}")
    result_label.config(text="\n".join(lines))


def show_chart():
    """
    Display 7-day price chart for selected coin.
    """
    sel = coin_combobox.get()
    cid = coin_dict.get(sel)
    if not cid:
        return
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart"
        params = {"vs_currency": "usd", "days": 7}
        data = requests.get(url, params=params).json()
        prices = data['prices']  # [ [timestamp, price], ... ]
    except Exception as e:
        messagebox.showerror("Hata", f"Grafik verisi alınamadı:\n{e}")
        return

    # Create plot
    vals  = [p[1] for p in prices]
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(vals)
    ax.set_title(f"{sel.split()[0]} - Son 7 Gün Fiyat")
    ax.set_ylabel('USD')
    ax.grid(True)

    # Embed in Tkinter
    chart_win = tk.Toplevel(root)
    chart_win.title(f"{sel.split()[0]} Fiyat Grafiği")
    canvas = FigureCanvasTkAgg(fig, master=chart_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)


# --- UI Setup ---
root = tk.Tk()
root.title("Coin Dönüştürücü")
root.geometry("500x500")

# Header
header = ttk.Label(root, text="Coin Dönüştürücü", font=("Helvetica", 18, "bold"))
header.pack(pady=10)

# Logo
logo_label = ttk.Label(root)
logo_label.pack(pady=5)

# Coin selection
frame_coin = ttk.Frame(root)
frame_coin.pack(fill='x', padx=20)
ttk.Label(frame_coin, text="Coin Seçiniz:", font=("Helvetica", 12)).pack(anchor='w')
coin_combobox = ttk.Combobox(frame_coin, state='readonly', font=("Helvetica", 12))
coin_combobox.pack(fill='x', pady=5)
coin_combobox.bind("<<ComboboxSelected>>", lambda e: update_logo(coin_combobox.get()))

# Amount entry
frame_amt = ttk.Frame(root)
frame_amt.pack(fill='x', padx=20)
ttk.Label(frame_amt, text="Miktar:", font=("Helvetica", 12)).pack(anchor='w')
amount_entry = ttk.Entry(frame_amt, font=("Helvetica", 12))
amount_entry.pack(fill='x', pady=5)

# Currency checkboxes
frame_cur = ttk.Labelframe(root, text="Para Birimleri", padding=10)
frame_cur.pack(fill='x', padx=20, pady=10)
var_usd = tk.IntVar(value=1)
var_eur = tk.IntVar(value=1)
var_try = tk.IntVar(value=1)
for txt, var in [("USD", var_usd), ("EUR", var_eur), ("TL", var_try)]:
    ttk.Checkbutton(frame_cur, text=txt, variable=var).pack(side='left', padx=10)

# Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=15)
convert_btn = ttk.Button(btn_frame, text="Dönüştür", command=convert_coin)
convert_btn.grid(row=0, column=0, padx=10)
chart_btn = ttk.Button(btn_frame, text="Grafiği Göster", command=show_chart)
chart_btn.grid(row=0, column=1, padx=10)

# Result label
result_label = ttk.Label(root, text="", font=("Helvetica", 14), justify='left')
result_label.pack(pady=10)

# Load initial data
load_coins()

root.mainloop()
