from datetime import datetime
from src.options import *

class Portfolio:
    def __init__(self, cash, time):
        self.time = time
        self.cash = cash
        self.all_assets = {}

    def add_asset(self, asset, price_paid, quantity):
        if (asset in self.all_assets.keys()):
            self.all_assets[asset] += quantity
        else:
            self.all_assets[asset] = quantity

        self.cash -= price_paid

    def remove_asset(self, asset, price_received, quantity):
        if (quantity < self.all_assets[asset]):
            self.all_assets[asset] -= quantity
        elif (quantity == self.all_assets[asset]):
            self.all_assets.pop(asset)

        self.cash += price_received

    def cash_amount(self):
        return self.cash

    def assets(self):
        assets_list = [key.get_name() for key in self.all_assets.keys()]
        return assets_list

    def summary(self):
        list = [[key.get_name(), self.all_assets[key]] for key in self.all_assets.keys() if key != "cash"]
        self.cash = round(self.cash, 2)
        list.append(["cash", self.cash])
        return list
    
    def valid_sell(self, asset, quantity):
        if asset in self.all_assets.keys():
            if self.all_assets[asset] >= quantity:
                return True
        else:
            return False
    
    def portfolio_value(self):
        value = self.cash
        
        for contract in self.all_assets.keys():
            value += self.all_assets[contract] * contract.get_adjusted_bid()
        
        return value
