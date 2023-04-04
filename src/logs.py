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

    def add_sequential(self, trade):
        if (trade.get_date() in self.orders_sequential.keys()):
            self.orders_sequential[trade.get_date()].append(trade)
        else:
            self.orders_sequential[trade.get_date()] = [trade]
            
    def add_ordered(self, trade):
        if (trade.get_date() in self.orders_files.keys()):
            if (trade.get_asset() in self.orders_files[trade.get_date()]):
                self.orders_files[trade.get_date()][trade.get_asset()].append(trade)
            else:
                self.orders_files[trade.get_date()][trade.get_asset()] = [trade]
        else:
            self.orders_files[trade.get_date()] = OrderedDict()
            self.orders_files[trade.get_date()][trade.get_asset()] = [trade]

    def get_sequential_raw(self):
        return self.orders_sequential

    def get_ordered_raw(self):
        return self.orders_files

    def get_ordered(self):
        copy = self.orders_files

        for date in copy.keys():
            for contract in copy[date].keys():
                for trade in copy[date][contract]:
                    trade = [trade.get_price_paid() * trade.get_quantity(), trade.get_order_type()]
                    print(trade)
        return copy