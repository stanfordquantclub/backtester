from datetime import datetime

from backtester.options import *

class Portfolio:
    def __init__(self, cash, time):
        self.time = time
        self.cash = cash
        self.all_assets = {}

    def buy_asset(self, asset, price_paid, quantity):
        if (asset in self.all_assets.keys()):
            self.all_assets[asset] += quantity
        else:
            self.all_assets[asset] = quantity
            
        self.cash -= price_paid

    def sell_asset(self, asset, price_received, quantity):
        if (quantity < self.all_assets[asset]):
            # Remove the quantity of the asset
            self.all_assets[asset] -= quantity
        elif (quantity == self.all_assets[asset]):
            # Remove the asset from the portfolio if the quantity is equal to the asset quantity
            self.all_assets.pop(asset)

        self.cash += price_received

    def get_cash(self):
        return self.cash
    
    def get_assets(self):
        return self.all_assets

    def assets(self):
        assets_list = [key.get_name() for key in self.all_assets.keys()]
        return assets_list

    def summary(self):
        list = [[key.get_name(), self.all_assets[key]] for key in self.all_assets.keys() if key != "cash"]
        self.cash = round(self.cash, 2)
        list.append(["cash", self.cash])
        return list
    
    def valid_sell(self, asset, quantity):
        # Check if the asset is in the portfolio and the asset quantity is greater than the quantity to be sold
        return asset in self.all_assets and self.all_assets[asset] >= quantity
    
    def portfolio_value(self):
        value = self.cash
        
        for contract in self.all_assets.keys():
            value += self.all_assets[contract] * contract.get_adjusted_bid()
        
        return value
