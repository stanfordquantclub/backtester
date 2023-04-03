from datetime import datetime

class Order:
    def __init__(self, contract_name, order_type, quantity, price_paid, id, date):
        """
        Args: contract_name (str): filepath to the contract that is being traded
              order_type (str): buy or sell indicating what action is being taken
              quantity (int): how many of a certain contract is being purchased
              price_paid (float): how much is being paid on a per contract basis
              id (int): unique id for each trade made
        """
        self.contract_name = contract_name
        self.order_type = order_type
        self.quantity = quantity
        self.price_paid = price_paid
        self.id = id

        #datetime object created from parsing the file path s
        self.date = date
        
    def get_date(self):
        return self.date

    def get_contract_name(self):
        return self.contract_name
    
    def get_order_type(self):
        return self.order_type
    
    def get_quantity(self):
        return self.quantity
    
    def get_price_paid(self):
        return self.price_paid
    
    def get_id(self):
        return self.id
    
    def get_date(self):
        return self.date
    
    
    
    

    