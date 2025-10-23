# Reexecutar após reset
import tkinter as tk
from tkinter import ttk

def criar_demo_widgets():
    root = tk.Tk()
    root.title("Demonstração de Widgets Tk e TTK")
    root.geometry("900x700")

    # Frames para organização
    frame_tk = tk.LabelFrame(root, text="tk (Tkinter Clássico)", padx=10, pady=10)
    frame_ttk = tk.LabelFrame(root, text="ttk (Themed Tkinter)", padx=10, pady=10)
    frame_tk.pack(padx=10, pady=10, fill="both", expand=True)
    frame_ttk.pack(padx=10, pady=10, fill="both", expand=True)

    # Widgets do Tkinter puro
    tk.Label(frame_tk, text="Label").grid(row=0, column=0, sticky="w")
    tk.Entry(frame_tk).grid(row=0, column=1)

    tk.Button(frame_tk, text="Button").grid(row=1, column=0)
    tk.Checkbutton(frame_tk, text="Checkbutton").grid(row=1, column=1)
    tk.Radiobutton(frame_tk, text="Radiobutton").grid(row=2, column=0)

    tk.Scale(frame_tk, from_=0, to=100, orient="horizontal").grid(row=2, column=1)
    tk.Listbox(frame_tk, height=3).grid(row=3, column=0)
    tk.Text(frame_tk, height=3, width=20).grid(row=3, column=1)

    tk.Spinbox(frame_tk, from_=0, to=10).grid(row=4, column=0)
    tk.Message(frame_tk, text="Mensagem longa que quebra linha automaticamente.").grid(row=4, column=1)

    # Widgets do ttk
    ttk.Label(frame_ttk, text="Label").grid(row=0, column=0, sticky="w")
    ttk.Entry(frame_ttk).grid(row=0, column=1)

    ttk.Button(frame_ttk, text="Button").grid(row=1, column=0)
    ttk.Checkbutton(frame_ttk, text="Checkbutton").grid(row=1, column=1)
    ttk.Radiobutton(frame_ttk, text="Radiobutton").grid(row=2, column=0)

    ttk.Combobox(frame_ttk, values=["Opção 1", "Opção 2"]).grid(row=2, column=1)
    ttk.Progressbar(frame_ttk, value=50, length=150).grid(row=3, column=0)

    tree = ttk.Treeview(frame_ttk, columns=("A", "B"), show="headings")
    tree.heading("A", text="Coluna A")
    tree.heading("B", text="Coluna B")
    tree.insert("", "end", values=("Item 1", "Valor 1"))
    tree.grid(row=3, column=1)
    tree.config()

    ttk.Separator(frame_ttk, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
    ttk.Notebook(frame_ttk, width=200, height=100).grid(row=5, column=0, columnspan=2)

    root.mainloop()

criar_demo_widgets()
