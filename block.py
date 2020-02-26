from time import time   # import voor de timestamp

class Block:
    def __init__(self, index, previous_hash, transactions, proof, timestamp=None): 
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time() if timestamp is None else timestamp   # de timestamp is de tijd op het moment van creatie van een block-instance, berekend door de geimporteerde time() functie
        self.transactions = transactions
        self.proof = proof
    

