import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter as tk
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from datetime import date
import os
import platform
import subprocess
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


import json
def load_services():
    if not os.path.exists("services.json"):
        # Create a basic default service list
        default_services = [
            {"name": "Consultation", "price": 100.00},
            {"name": "Bug Fixing", "price": 75.00}
        ]
        with open("services.json", "w") as f:
            json.dump(default_services, f, indent=4)
        return default_services
    with open("services.json", "r") as f:
        return json.load(f)

services_data = load_services()

selected_services = []
def update_service_dropdown():
    service_dropdown['values'] = [f"{s['name']} - ${s['price']:.2f}" for s in services_data]

# ----- Add Service to List -----
def add_service():
    selected = service_dropdown.current()
    if selected != -1:
        service = services_data[selected]
        desc, price = service["name"], service["price"]
        selected_services.append((desc, price))
        listbox.insert("end", f"{desc} - ${price:.2f}")
        update_total()

# ----- Update Total -----
def update_total():
    total = sum(price for _, price in selected_services)
    total_label.config(text=f"Total: ${total:.2f}")

# ----- Generate Invoice PDF -----
def generate_invoice():
    company_name = company_entry.get().strip() or "Your Company"
    save_config({"company_name": company_name})


    client_name = client_entry.get().strip()

    if not client_name:
        messagebox.showwarning("Missing Info", "⚠️ Please enter a client name.")
        return

    if not selected_services:
        messagebox.showwarning("Missing Info", "⚠️ Please add at least one service.")
        return

    today = date.today()
    safe_client = client_name.replace(" ", "_")
    import os  # if not already imported

    # Ensure invoices folder exists
    invoice_dir = "invoices"
    os.makedirs(invoice_dir, exist_ok=True)
    filename = os.path.join(invoice_dir, f"Invoice_{safe_client}_{today}.pdf")
    
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER

    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 60, "INVOICE")
    c.line(50, height - 70, width - 50, height - 70)

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Bill To: {client_name}")
    c.drawString(50, height - 120, f"Issued By: {company_name}")
    c.drawString(50, height - 140, f"Date: {today.strftime('%B %d, %Y')}")

    y = height - 180
    total = 0

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Service")
    c.drawString(400, y, "Price")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20

    c.setFont("Helvetica", 12)
    for desc, price in selected_services:
        c.drawString(50, y, desc)
        c.drawRightString(450, y, f"${price:.2f}")
        total += price
        y -= 20

    y -= 10
    c.line(50, y, width - 50, y)
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Total Due:")
    c.drawRightString(450, y, f"${total:.2f}")
    c.save()

    messagebox.showinfo("Success", f"✅ Invoice saved as {filename}")

    # Open the PDF
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        subprocess.call(["open", filename])
    else:
        subprocess.call(["xdg-open", filename])

    # Reset
    client_entry.delete(0, "end")
    listbox.delete(0, "end")
    selected_services.clear()
    update_total()
    status_label.config(text="")


# ----- GUI Setup -----
root = ttk.Window(themename="flatly")
root.title("Invoice Generator")
#root.geometry("600x550")

root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

ttk.Label(frame, text="Client Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
client_entry = ttk.Entry(frame, width=40)
client_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Your Company Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
company_entry = ttk.Entry(frame, width=40)
company_entry.grid(row=1, column=1, padx=5, pady=5)

config = load_config()
last_company = config.get("company_name", "")
company_entry.delete(0, "end")  # clear just in case
company_entry.insert(0, last_company)

ttk.Label(frame, text="Select a service:").grid(row=2, column=0, sticky="w", padx=5, pady=5)

service_var = ttk.StringVar()
service_dropdown = ttk.Combobox(frame, textvariable=service_var, state="readonly", width=30)
service_dropdown['values'] = [f"{s['name']} - ${s['price']:.2f}" for s in services_data]
service_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="w")

add_btn = ttk.Button(frame, text="Add Service", command=add_service)
add_btn.grid(row=3, column=1, sticky="w", padx=5)

services_frame = ttk.LabelFrame(frame, text="Selected Services")
services_frame.grid(row=4, column=0, columnspan=2, pady=(10, 5), sticky="ew")

listbox = tk.Listbox(services_frame, height=8, width=55)

listbox.pack(padx=10, pady=5)

total_label = ttk.Label(frame, text="Total: $0", font=("Segoe UI", 11, "bold"))
total_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))

generate_btn = ttk.Button(frame, text="Generate Invoice", command=generate_invoice)
generate_btn.grid(row=6, column=0, columnspan=2, pady=10)

status_label = ttk.Label(frame, text="", foreground="green")
status_label.grid(row=7, column=0, columnspan=2, sticky="w")

def open_service_editor(on_update_callback):
    editor = tk.Toplevel(root)
    editor.title("Edit Services")
    editor.geometry("450x500")
    editor.minsize(700, 800)  # Prevent it from being squished

    editor.grab_set()  # Prevent interaction with main window

    def refresh_service_list():
        listbox.delete(0, "end")
        for s in services_data:
            listbox.insert("end", f"{s['name']} - ${s['price']:.2f}")

    def save_services():
        with open("services.json", "w") as f:
            json.dump(services_data, f, indent=4)
        service_dropdown['values'] = [f"{s['name']} - ${s['price']:.2f}" for s in services_data]
 
        refresh_service_list()
    on_update_callback()

    def add_service_modal():
        name = name_entry.get().strip()
        price = price_entry.get().strip()

        if not name or not price:
            messagebox.showerror("Error", "Name and price required")
            return

        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number")
            return

        services_data.append({"name": name, "price": price})
        save_services()

    def delete_selected():
        selected = listbox.curselection()
        if not selected:
            return
        index = selected[0]
        del services_data[index]
        save_services()

    listbox = tk.Listbox(editor)
    listbox.pack(padx=10, pady=10, fill="both", expand=True)

    name_entry = ttk.Entry(editor)
    name_entry.pack(padx=10, pady=(5, 0))
    name_entry.insert(0, "Service Name")

    price_entry = ttk.Entry(editor)
    price_entry.pack(padx=10, pady=(5, 10))
    price_entry.insert(0, "0.00")

    button_frame = ttk.Frame(editor)
    button_frame.pack(pady=5)

    ttk.Button(button_frame, text="Add", command=add_service_modal).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Delete", command=delete_selected).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Close", command=editor.destroy).grid(row=0, column=2, padx=5)

    refresh_service_list()
edit_btn = ttk.Button(frame, text="Edit Services", command=lambda: open_service_editor(update_service_dropdown))
edit_btn.grid(row=5, column=1, sticky="e", padx=5)

root.mainloop()
