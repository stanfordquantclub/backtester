from datetime import datetime
from src.options import *

class Portfolio:
    def __init__(self, cash):
        self.all_assets = {"cash": cash}

    def add_asset(self, asset, quantity):
        if (asset in self.all_assets.keys()):
            self.all_assets[asset] += quantity
        else:
            self.all_assets[asset] = quantity

    def cash_amount(self):
        return self.all_assets["cash"]
    



    