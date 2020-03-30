from collections import OrderedDict 

class Transaction:
    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
    

    def __repr__(self):
        return f"Sender: {self.sender}, Recipient: {self.recipient}, Amount: {self.amount}, Signature: {self.signature}"
    
    
    def to_ordered_dict(self):
        """ Returns an OrderedDict object """
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('signature', self.signature), ('amount', self.amount)])
    

    


