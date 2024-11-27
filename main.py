import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BillingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Billing System")
        self.root.geometry("800x700")

        self.billNumber = tk.StringVar(value=f"BN-{random.randint(1000,10000)}")
        self.date = tk.StringVar(value=datetime.now().strftime('%d-%m-%Y'))
        self.time = tk.StringVar(value=datetime.now().strftime('%H:%M'))
        self.selectedItem = tk.StringVar()
        self.quantity = tk.IntVar(value=1)
        self.price = tk.DoubleVar(value=0.0)
        self.totalBill = tk.DoubleVar(value=0.0)
        self.paymentType = tk.StringVar()

        self.orderItem = []

        self.menu = {
            "Water bottle": 20, "Chai": 20, "Coffee": 25,
            "Roti": 20, "Chapati": 10, "Nan": 30, "Butter Nan": 35,
            "Panner Masala": 150, "Paalak Paneer": 160, "Maharaja Paneer": 200,
            "Fish Masala": 210, "Chicken Handi": 300, "Butter Chicken": 350
        }

        self.createWidget()
        self.createDatabase()

    def createDatabase(self):
        """ Create SQLite database for storing orders """
        self.conn = sqlite3.connect('billing_system.db')
        self.cursor = self.conn.cursor()

        # Create table for storing orders if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                bill_number TEXT,
                item TEXT,
                quantity INTEGER,
                price REAL,
                date TEXT,
                time TEXT,
                payment_type TEXT
            )
        ''')
        self.conn.commit()

    def createWidget(self):
        tk.Label(self.root, text="Billing System", font="Arial 15 bold").pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        date = tk.Label(frame, text=f"Date: ", font="Arial 12")
        date.grid(row=0, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.date).grid(row=0, column=1, sticky="w", padx=5)

        time = tk.Label(frame, text=f"Time: ", font="Arial 12")
        time.grid(row=1, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.time).grid(row=1, column=1, sticky="w", padx=5)

        bill = tk.Label(frame, text="Bill No:", font="Arial 12")
        bill.grid(row=2, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.billNumber).grid(row=2, column=1, sticky='w', padx=5)

        menu = tk.Label(frame, text="Menu:", font="Arial 12")
        menu.grid(row=3, column=0, sticky="w")
        combobox = ttk.Combobox(frame, textvariable=self.selectedItem, values=list(self.menu.keys()), state="readonly")
        combobox.grid(row=3, column=1, sticky="w", padx=5)
        combobox.bind("<<ComboboxSelected>>", self.updatePrice)  # Automatically update price when item is selected

        quantity = tk.Label(frame, text="Quantity:", font="Arial 12")
        quantity.grid(row=4, column=0, sticky='w')
        quantity_entry = tk.Entry(frame, textvariable=self.quantity)
        quantity_entry.grid(row=4, column=1, sticky='w', padx=5)
        quantity_entry.bind("<KeyRelease>", self.updatePrice)  # Automatically update price when quantity changes

        price = tk.Label(frame, text="Price:", font="Arial 12")
        price.grid(row=5, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.price, state='readonly').grid(row=5, column=1, sticky='w', padx=5)

        buttonFrame = tk.Frame(self.root)
        buttonFrame.pack(pady=8)

        update = tk.Button(buttonFrame, text="Update Item", bg="#1874CD", borderwidth=0, fg="white", command=self.updatePrice).pack(side="left", padx=5)
        add = tk.Button(buttonFrame, text="Add Item", bg="light green", borderwidth=0, fg="white", command=self.addOrder).pack(side="left", padx=5)
        delete = tk.Button(buttonFrame, text="Delete Item", bg="#FF4040", borderwidth=0, fg="white", command=self.deleteOrder).pack(side="left", padx=5)

        self.orderList = ttk.Treeview(self.root, columns=("items", "quantity", "price"), show="headings", height=10)
        self.orderList.heading("items", text="ITEMS")
        self.orderList.heading("quantity", text="QUANTITY")
        self.orderList.heading("price", text="PRICE")
        self.orderList.pack(pady=10)

        totalFrame = tk.Frame(self.root)
        totalFrame.pack(pady=5)

        totalCost = tk.Label(totalFrame, text="Total:", font="Arial 12")
        totalCost.grid(row=0, column=0, sticky='w', padx=5)
        tk.Entry(totalFrame, textvariable=self.totalBill, state="readonly").grid(row=0, column=1, sticky="w", padx=5)
        payment = tk.Label(totalFrame, text="Payment Type:")
        payment.grid(row=0, column=2, sticky="w", padx=5)
        ttk.Combobox(totalFrame, textvariable=self.paymentType, values=["Card", "Cash", "UPI"], state="readonly").grid(row=0, column=3)

        orderButton = tk.Button(self.root, text="Order Now!", font="Arial 12", bg="green", fg="White", borderwidth=0, command=self.orderNow)
        orderButton.pack(pady=5)

        graphButton = tk.Button(self.root, text="View Sales Graph", font="Arial 12", bg="#FF34B3", fg="white", borderwidth=0, command=self.viewSalesGraph)
        graphButton.pack(pady=5)

    def updatePrice(self, event=None):
        item = self.selectedItem.get()
        quantity = self.quantity.get()

        if item in self.menu and quantity > 0:
            price = self.menu[item] * quantity
            self.price.set(price)

    def addOrder(self):
        item = self.selectedItem.get()
        quantity = self.quantity.get()
        price = self.price.get()

        if item and quantity > 0 and price > 0:
            self.orderItem.append((item, quantity, price))
            self.orderList.insert("", "end", values=(item, quantity, price))
            self.calculateTotal()

    def deleteOrder(self):
        selected = self.orderList.selection()
        if selected:
            for sel in selected:
                self.orderList.delete(sel)
                values = self.orderList.item(sel)["values"]
                self.orderItem.remove(tuple(values))
            self.calculateTotal()

    def calculateTotal(self):
        total = sum(item[2] for item in self.orderItem)
        self.totalBill.set(total)

    def orderNow(self):
        if self.paymentType.get():
            # Insert order into database
            bill_number = self.billNumber.get()
            date = self.date.get()
            time = self.time.get()
            payment_type = self.paymentType.get()

            for item, quantity, price in self.orderItem:
                self.cursor.execute('''
                    INSERT INTO orders (bill_number, item, quantity, price, date, time, payment_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (bill_number, item, quantity, price, date, time, payment_type))
            
            self.conn.commit()

            messagebox.showinfo("Order Placed", f"Thank you!, keep visiting \nTotal : {self.totalBill.get()}")
        else:
            messagebox.showerror("Error", "Please select the payment type!")



if __name__ == "__main__":
    window = tk.Tk()
    BillingSystem(window)
    window.mainloop()


