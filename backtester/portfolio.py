from datetime import datetime

class Portfolio:
    def __init__(self, cash, time):
        self.time = time
        self.cash = cash
        self.all_assets = {}

    def set_time(self, time):
        self.time = time

    def get_cash(self):
        return self.cash
    
    def get_assets(self):
        return self.all_assets
    
    def get_value(self):
        """
        Gets the value of the portfolio
        
        Returns:
            float: value of the portfolio
        """
        value = self.cash # Current liquid cash
        
        # Calculate the value of the portfolio
        for asset in self.all_assets:
            value += self.all_assets[asset] * asset.get_adjusted_bid()
        
        return value
    
    def buy_asset(self, asset, price_paid, quantity):
        """
        Buy an asset and add it to the portfolio
        
        Parameters:
            asset (Contract): The asset to buy
            price_paid (float): The price paid for the asset
            quantity (int): The quantity of the asset to buy
        """
        if asset in self.all_assets:
            self.all_assets[asset] += quantity
        else:
            self.all_assets[asset] = quantity
            
        self.cash -= price_paid

    def sell_asset(self, asset, price_received, quantity):
        """
        Sell an asset and remove it from the portfolio if the quantity is zero
        
        Parameters:
            asset (Contract): The asset to sell
            price_received (float): The price received for the asset
            quantity (int): The quantity of the asset to sell
        """
        if (quantity < self.all_assets[asset]):
            # Remove the quantity of the asset
            self.all_assets[asset] -= quantity
        elif (quantity == self.all_assets[asset]):
            # Remove the asset from the portfolio if the quantity is equal to the asset quantity
            self.all_assets.pop(asset)

        self.cash += price_received

    def assets(self):
        assets_list = [asset.get_name() for asset in self.all_assets]
        return assets_list

    def summary(self):
        list = [[asset.get_name(), self.all_assets[asset]] for asset in self.all_assets if asset != "cash"]
        self.cash = round(self.cash, 2)
        list.append(["cash", self.cash])
        return list
    
    def valid_sell(self, asset, quantity):
        """
        Check if the asset is in the portfolio and the asset quantity is greater than the quantity to be sold

        Args:
            asset (Contract): asset to be sold
            quantity (int): amount of asset to be sold

        Returns:
            bool: whether it's a valid sell or not
        """
        
        # Check if the asset is in the portfolio and the asset quantity is greater than the quantity to be sold
        if asset not in self.all_assets:
            formatted_date_time = datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"<Log:{formatted_date_time}> Asset {asset} not in portfolio")
            return False
        
        elif self.all_assets[asset] < quantity:
            formatted_date_time = datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"<Log:{formatted_date_time}> Not enough {asset} in portfolio to sell")
            return False
        
        return True