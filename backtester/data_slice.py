import sys

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

    def __sizeof__(self):
        # Recursively get the size of all the chains and underlying
        size = sys.getsizeof(self.chains) + sys.getsizeof(self.underlying)
        
        for chain in self.chains.values():
            size += chain.__sizeof__()
            
        for underlying in self.underlying.values():
            size += underlying.__sizeof__()
            
        return size
