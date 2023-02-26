import pandas_market_calendars as mcal

from datetime import date
import pytz
import glob
from utils import Slice
import pandas as pd
import logs 
import statistics

class Engine: 
    def initialize_defaults(self, security_name: str=None, start_cash: float=None, start_date:date=None, end_date:date=None, path_dates=None, filter_paths=None, timezone="US/Eastern", root_path="/srv/sqc/data/us-options-tanq"):
        """
        Args:
            security_name (str): name of the security to backtest
            start_date (date): start date of the backtest
            end_date (date): end date of the backtest
            path_dates (list[str]): list of paths to use for the backtest - if this is used, start_date and end_date are ignored
            filter (str): filter to use when generating paths within the start_date and end_date or path_dates
            start_cash (float): starting cash for the backtest
        """
        print("Initialize Defaults")
        
        self.security_name = security_name
        
        self.start_date = start_date
        self.end_date = end_date
        self.path_dates = path_dates
        
        self.filter_paths = filter_paths
        self.root_path = root_path
        self.timezone = timezone
        self.start_cash = start_cash
        self.current_cash = start_cash

        #[[trading_day_1 {file_name: [trade_1 [buy [price, number_of_contracts], sell [price, number_of_contracts] ] ] , file_name}], [trading_day_2 {}], ]

        self.logs = logs()
        self.trades = []
        self.sharpe_ratio = 1
        self.sortino_ratio = 1
        self.total_return = 0
        
    
    def initialize(self):
        """
        Method is to be overriden by subclass
        """
        print("Initialize Engine")
        pass

    def get_data_paths(self):
        """
        Args:
            start (date): start date of the backtest
            end (date): end date of the backtest
            paths (list[str]): list of paths to use for the backtest - if this is used, start and end are ignored
        
        Returns:
            list[str]: list of paths to the data
        """
        
        if self.path_dates:
            return self.path_dates
        
        if self.start_date and self.end_date:
            data_paths = []

            nyse = mcal.get_calendar('NYSE')
            
            schedule = nyse.schedule(self.start_date, self.end_date)

            schedule["market_open"] = schedule["market_open"].dt.tz_convert(pytz.timezone(self.timezone))
            schedule["market_close"] = schedule["market_close"].dt.tz_convert(pytz.timezone(self.timezone))

            for day, (open_date, close_date) in schedule.iterrows():
                data_path = f"{self.root_path}/us-options-tanq-{open_date.year}/{open_date.strftime('%Y%m%d')}/{self.security_name[0]}/{self.security_name}/*/*"

                data_path_contracts = glob.glob(data_path)
                print(data_path_contracts)
                if self.filter_paths:
                    data_path_contracts = [contract for contract in data_path_contracts if self.filter_paths in contract] 

                data_paths.extend(data_path_contracts)

            return data_paths

    def on_data(self, data: Slice):
        """
        Method is to be overriden by subclass
        
        Args:
            data (Slice): data slice of the csv data
        """
        pass

    def back_test(self):
        self.initialize_defaults()
        self.initialize()
        
        data_paths = self.get_data_paths()
        
        for paths in data_paths:
            df = pd.read_csv(paths)
            
            for (idx, row) in df.iterrows():
                data_slice = Slice(row.index, row)
                self.on_data(data_slice)

    """
    gets the total return on the portfolio
    """
    def total_return(self):
        self.total_return =  ((self.current_cash - self.start_cash)/ self.start_cash) * 100

    def calculate_trades(self):
        ordered_trades = self.logs.get_trades()
        traded_contracts = list(ordered_trades.keys())
        
        

        for contract in traded_contracts:
            #the trades_made within one contract
            trades_made = ordered_trades[contract]
            
            ind = 0
            while (len(trades_made != 0)):
                if (trades_made[ind].get_order_type != trades_made[ind + 1].get_order_type):
                    self.trades.append((trades_made[ind + 1].get_price_paid() - trades_made[ind].get_price_paid()) / trades_made[ind])
                    del trades_made[ind]
                    del trades_made[ind]
        
            
    def sharpe_ratio(self):
        standard_dev = statistics.stdev(self.trades)
        return self.total_return / standard_dev
    
    
        
                        




