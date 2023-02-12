import pandas_market_calendars as mcal
from datetime import date
import pytz

class Engine: 
    def __init__(self, security_name, start_cash, start_date=None, end_date=None, path_dates=None, filter=None, timezone="America/New_York", root_path="/srv/sqc/data/us-options-tanq"):
        """
        Args:
            security_name (str): name of the security to backtest
            start_date (date): start date of the backtest
            end_date (date): end date of the backtest
            path_dates (list[str]): list of paths to use for the backtest - if this is used, start_date and end_date are ignored
            filter (str): filter to use when generating paths within the start_date and end_date or path_dates
            start_cash (float): starting cash for the backtest
        """
        
        self.security = security_name
        
        self.start_date = start_date
        self.end_date = end_date
        self.path_dates = path_dates
        self.filter = filter
        
        self.start_cash = start_cash
        
        self.schedule = self.get_data()

    def get_data(self):
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

            schedule["market_open"] = schedule["market_open"].dt.tz_convert(pytz.timezone('US/Eastern'))
            schedule["market_close"] = schedule["market_close"].dt.tz_convert(pytz.timezone('US/Eastern'))

            for day, (open_date, close_date) in schedule.iterrows():
                print(open_date, close_date)
            
            
            # if self.filter:
            #     schedule = schedule[schedule["market_open"].dt.strftime("%Y%m%d") == self.filter]

            return data_paths

    def onData(self, data):
        # for day in self.schedule()   
        #     for second in 
        pass

    def run(self):
        data_paths = self.get_data()
        
        for paths in data_paths:
            file = open(paths, "r")
            for data in file:
                self.onData(data)
