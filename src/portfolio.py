from datetime import datetime
from src.options import *

class Portfolio:
    def __init__(self, cash, time):
        self.time = time
        self.all_assets = {"cash": cash}

    def add_asset(self, asset, price_paid, quantity):
        if (asset in self.all_assets.keys()):
            self.all_assets[asset] += quantity
        else:
            self.all_assets[asset] = quantity

        self.all_assets["cash"] -= quantity * price_paid

    def remove_asset(self, asset, price_received, quantity):
        assert quantity <= self.all_assets[asset], "Selling more than owned"
        
        if (quantity < self.all_assets[asset]):
            self.all_assets[asset] -= quantity
        elif (quantity == self.all_assets[asset]):
            self.all_assets.pop(asset)

        self.all_assets["cash"] += quantity * price_received

    def cash_amount(self):
        return self.all_assets["cash"]

    def assets(self):
        assets_list = [key.get_name() for key in self.all_assets.keys() if key != "cash"]
        return assets_list

    def summary(self):
        list = [[key.get_name(), self.all_assets[key]] for key in self.all_assets.keys() if key != "cash"]
        self.all_assets["cash"] = round(self.all_assets["cash"], 2)
        list.append(["cash", self.all_assets["cash"]])
        return list
    
    def valid_sell(self, asset, quantity):
        if asset in self.all_assets.keys():
            if self.all_assets[asset] >= quantity:
                return True
        else:
            return False
    

    def portfolio_value(self):
        value = self.all_assets["cash"]
        
        for contract in self.all_assets.keys():
            if contract != "cash":
                value += self.all_assets[contract] * contract.get_bid_max_price()
        
        return value

    
    



    