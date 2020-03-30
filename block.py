from time import time   

class Block:
    def __init__(self, index, previous_hash, transactions, proof, timestamp=None): 
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time() if timestamp is None else timestamp   
        self.transactions = transactions
        self.proof = proof
    

    def __repr__(self):
        return f"Index: {self.index}, Previous Hash: {self.previous_hash}, Proof: {self.proof}, Timestamp: {self.timestamp}, Transactions: {self.transactions}"
