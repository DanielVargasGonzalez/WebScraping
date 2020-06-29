#!/usr/bin/env python3
import tkinter as tk
import scraping_libertad_digital
import scraping_okdiario

HEIGHT = 500
WIDTH = 600


def test_function(entry):
    my_list = entry.split(",")
    scraping_okdiario.pipeline(my_list)
    scraping_libertad_digital.pipeline(my_list)
    label.config(text="proceso completado")

root = tk.Tk()

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

background_image = tk.PhotoImage(file='background.png')
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg='#80c1ff', bd=5)
frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.1, anchor='n')

entry = tk.Entry(frame, font=40)
entry.place(relwidth=0.65, relheight=1)

button = tk.Button(frame, text="Buscar", font=40, command=lambda: test_function(entry.get()))
button.place(relx=0.7, relheight=1, relwidth=0.3)

lower_frame = tk.Frame(root, bg='#80c1ff', bd=10)
lower_frame.place(relx=0.5, rely=0.25, relwidth=0.75, relheight=0.6, anchor='n')

global label
label = tk.Label(lower_frame, text="introduzca las palabras que quiera buscar")
label.place(relwidth=1, relheight=1)

root.mainloop()
