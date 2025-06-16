import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

global_max_bounds = {'min_x': float('inf'), 'max_x': float('-inf'),
                     'min_y': float('inf'), 'max_y': float('-inf')}

def map(wert, alt_min=0, alt_max=100, neu_min=0, neu_max=100):
    return (wert - alt_min) / (alt_max - alt_min) * (neu_max - neu_min) + neu_min

def berechne_trapezpunkte(basis, hoehe, winkel_grad):
    """Berechnet die Koordinaten eines gleichschenkligen Trapezes mit gegebener Basis, Höhe und Winkel der Schenkel"""
    winkel_rad = math.radians(winkel_grad)
    delta = hoehe / math.tan(winkel_rad)
    oben = basis - 2 * delta
    return [(0, 0), (basis, 0), (basis - delta, hoehe), (delta, hoehe)]

def berechne_grundflaechenlaenge(start_basis, scale_factor, anzahl):
    if scale_factor == 1:
        return start_basis * anzahl
    else:
        return start_basis * (1 - scale_factor ** anzahl) / (1 - scale_factor)
    
def rotiere_punkte(punkte, winkel_grad, drehpunkt):
    """Rotiert eine Liste von Punkten um einen gegebenen Punkt"""
    winkel_rad = math.radians(winkel_grad)
    cos_w = math.cos(winkel_rad)
    sin_w = math.sin(winkel_rad)
    dx, dy = drehpunkt
    neue_punkte = []
    for x, y in punkte:
        x -= dx
        y -= dy
        x_rot = x * cos_w - y * sin_w
        y_rot = x * sin_w + y * cos_w
        neue_punkte.append((x_rot + dx, y_rot + dy))
    return neue_punkte

def berechne_maximale_bounds():
    global_max_bounds = {0,0,0,0}
    basis = grundflaeche_slider.get()
    hoehe = hoehe_slider.get()
    schenkel = schenkel_slider.get()
    anzahl = anzahl_slider.get()
    percentage = percent_slider.get() / 100.0

    winkelwerte = [0, 50, 100]
    global global_max_bounds

    for winkel_slider_wert in winkelwerte:
        winkel = (90 - schenkel) * winkel_slider_wert / 50
        aktuelle_position = (0, 0)
        aktuelle_rotation = 0
        aktuelle_basis = basis
        aktuelle_hoehe = hoehe

        alle_x, alle_y = [], []

        for _ in range(anzahl):
            trapez = berechne_trapezpunkte(aktuelle_basis, aktuelle_hoehe, schenkel)
            punkte_rotiert = rotiere_punkte(trapez, aktuelle_rotation, (0, 0))
            punkte_final = [(x + aktuelle_position[0], y + aktuelle_position[1]) for x, y in punkte_rotiert]

            xs, ys = zip(*punkte_final)
            alle_x.extend(xs)
            alle_y.extend(ys)

            punkt_B = punkte_final[1]
            aktuelle_position = punkt_B
            aktuelle_rotation += winkel
            aktuelle_basis *= percentage
            aktuelle_hoehe *= percentage

        if alle_x and alle_y:
            global_max_bounds['min_x'] = min(global_max_bounds['min_x'], min(alle_x))
            global_max_bounds['max_x'] = max(global_max_bounds['max_x'], max(alle_x))
            global_max_bounds['min_y'] = min(global_max_bounds['min_y'], min(alle_y))
            global_max_bounds['max_y'] = max(global_max_bounds['max_y'], max(alle_y))


def zeichne_trapeze(_=None):
    berechne_maximale_bounds()

    basis = grundflaeche_slider.get()
    hoehe = hoehe_slider.get()
    schenkel = schenkel_slider.get()
    anzahl = anzahl_slider.get()
    winkel = (90 - schenkel) * winkel_slider.get() / 50
    percentage = percent_slider.get() / 100.0

    gesamtlaenge = berechne_grundflaechenlaenge(basis, percentage, anzahl)
    info_label.config(text=f"Gesamtlänge: {gesamtlaenge:.2f}")

    fig.clear()
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.tick_params(labelsize=8)

    aktuelle_position = (0, 0)
    aktuelle_rotation = 0
    aktuelle_basis = basis
    aktuelle_hoehe = hoehe

    for _ in range(anzahl):
        trapez = berechne_trapezpunkte(aktuelle_basis, aktuelle_hoehe, schenkel)
        punkte_rotiert = rotiere_punkte(trapez, aktuelle_rotation, (0, 0))
        punkte_final = [(x + aktuelle_position[0], y + aktuelle_position[1]) for x, y in punkte_rotiert]

        geschlossene_form = punkte_final + [punkte_final[0]]
        xs, ys = zip(*geschlossene_form)
        ax.plot(xs, ys, 'b')

        punkt_B = punkte_final[1]
        aktuelle_position = punkt_B
        aktuelle_rotation += winkel
        aktuelle_basis *= percentage
        aktuelle_hoehe *= percentage

    # === Dynamischer Bereich mit fixen globalen Maximalgrenzen ===
    min_x = global_max_bounds['min_x']
    max_x = global_max_bounds['max_x']
    min_y = global_max_bounds['min_y']
    max_y = global_max_bounds['max_y']

    width = max_x - min_x
    height = max_y - min_y
    pad_x = width * 0.1
    pad_y = height * 0.1

    width += 2 * pad_x
    height += 2 * pad_y
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    target_ratio = 4 / 3
    actual_ratio = width / height

    if actual_ratio > target_ratio:
        new_height = width / target_ratio
        pad_y = (new_height - height) / 2
        height = new_height
    else:
        new_width = height * target_ratio
        pad_x = (new_width - width) / 2
        width = new_width

    ax.set_xlim(center_x - width / 2, center_x + width / 2)
    ax.set_ylim(center_y - height / 2, center_y + height / 2)

    canvas.draw()


# GUI erstellen
root = tk.Tk()
root.title("Trapez Generator")

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
def add_slider(name, from_, to, initial, variable_ref):
    row = ttk.Frame(frame)
    row.pack(fill=tk.X, pady=2)

    ttk.Label(row, text=name, width=15).pack(side=tk.LEFT)
    slider = tk.Scale(row, from_=from_, to=to, orient=tk.HORIZONTAL, command=zeichne_trapeze)
    slider.set(initial)
    slider.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    variable_ref.append(slider)

slider_refs = []

add_slider("Grundfläche", 0, 40, 18, slider_refs)
add_slider("Höhe", 0, 30, 14, slider_refs)
add_slider("Schenkel (°)", 60, 90, 75, slider_refs)
add_slider("Percentage", 80, 100, 95, slider_refs)
add_slider("Anzahl Trapeze", 1, 30, 15, slider_refs)
add_slider("Winkel", 0, 100, 0, slider_refs)

grundflaeche_slider, hoehe_slider, schenkel_slider, percent_slider, anzahl_slider, winkel_slider = slider_refs

info_label = ttk.Label(frame, text="Gesamtlänge: 0")
info_label.pack(pady=10)

# Matplotlib Canvas
fig = plt.Figure(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


zeichne_trapeze()

root.mainloop()
