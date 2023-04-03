from collections import OrderedDict

class Logs:
    def __init__(self):
        """
        Args: none

        self.orders_sequential - all trades listed in the order that they are placed, separated by days which act as dictionary keys
        self.orders_files - trades organized by what contracts are being traded, separated by keys which are file names
        """
        self.orders_sequential = OrderedDict()
        self.orders_files = OrderedDict()

    def add_trade(self, date, trade):
        if (trade.get_contract_name() in self.orders_files):
            self.orders_files[trade.get_contract_name()].append(trade)
        else: 
            self.orders_files[trade.get_contract_name()] = [trade]

    def add_sequential(self, trade):
        if (trade.get_date() in self.orders_sequential.keys()):
            self.orders_sequential[trade.get_date()].append(trade)
        else:
            self.orders_sequential[trade.get_date()] = []
            