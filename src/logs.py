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
            
    
    def add_orders_files(self, date, trade):
        """
        Args: trade (order obj): order object that holds the trade that is being added to the log
        """
        if (trade.get_contract_name() in self.orders_files):
            self.orders_files[trade.get_contract_name()].append(trade)
        else: 
            self.orders_files[trade.get_contract_name()] = [trade]

    def get_sequential_log(self):
        """
        returns: dict[keys (trading days): value(list[order objects in sequential order])]
        """
        return self.orders_sequential

    def get_trades(self):
        """
        returns: dict[keys (contract names): value(list[order objects in sequential order])]
        """
        return self.orders_files