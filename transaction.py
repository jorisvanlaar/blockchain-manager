from collections import OrderedDict # geimporteerd om ervoor te zorgen dat al je transaction dictionaries een vaste volgorder/order krijgen

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
    
    
    # Je bouwt een Transaction op met een OrderedDict om ervoor te zorgen dat de order van je transactions altijd vaststaat. 
    # Dit is nodig zodat je dan altijd dezelfde correcte hash genereert voor eenzelfde block in de valid_proof() method
    # Een OrderedDict is opgebouwd uit een list aan tuples, waarbij elke tuple een key-value pair is.
    # Door deze functie hier in te bouwen kun je wanneer je wilt makkelijk een Transaction object converten naar een OrderedDict, om zo dus de order te waarborgen.
    def to_ordered_dict(self):
        """ Returns an OrderedDict object """
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])


