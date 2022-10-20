#!usr/bin/env python3
from flask_table import Table, Col

# declear Table
class ItemTable(Table):
    category = Col("Category")
    price = Col("Price")
    quantity = Col("Quantity")
    subtotal = Col("Subtotal")
    delete = Col("Delete")

# get object
class Item(object):
    def __init__(self, category, quantity, price, subtotal, delete):
        self.category = category
        self.price = price
        self.quantity = quantity
        self.subtotal = subtotal
        self.delete = delete
