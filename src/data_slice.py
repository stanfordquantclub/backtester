class Slice:
    """
    This class formats row data from the csv. Used by the on_data method in 
    Engine to pass data to the strategy.
    """
    def __init__(self) -> None:
        self.chains = {}
        self.underlying = {}
        
    def add_underlying(self, underlying):
        self.underlying[underlying.asset] = underlying
        
    def get_underlying(self, asset_name):
        return self.underlying[asset_name]
        
    def add_chain(self, chain):
        self.chains[chain.asset] = chain
        
    def get_chain(self, asset_name):
        return self.chains[asset_name]
