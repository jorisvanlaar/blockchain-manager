import hashlib
import json
from block import Block
from transaction import Transaction
from helpers.hash_util import hash_block        
from helpers.verification import Verification
from wallet import Wallet

MINING_REWARD = 10  

class Blockchain:
    def __init__(self, hosting_node_id):    
        genesis_block = Block(0, '', [], 100, 0)    
        self.__chain = [genesis_block]              
        self.__open_transactions = []               
        self.load_data()                            
        self.hosting_node = hosting_node_id         

    
    @property
    def chain(self):
        return self.__chain[:]  
    
    
    @chain.setter
    def chain(self, value):
        self.__chain = value
    

    @property
    def open_transactions(self):
        return self.__open_transactions[:]  


    @open_transactions.setter
    def open_transactions(self, value):
        self.__open_transactions = value


    def load_data(self):
        """ Opens the blockchain & open transactions from a file an initializes the blockchain and open transactions """
        try:
            with open('blockchain.txt', 'r') as file:
                file_content = file.readlines()                     
                blockchain = json.loads(file_content[0][:-1])       
                updated_blockchain = []
                
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]   
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
            
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])  
                updated_transactions.append(updated_transaction)
            self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            print('Could not load data')
    

    def save_data(self):
        """ Stores the blockchain and open transactions in a file """
        try:
            with open('blockchain.txt', 'w') as file:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,[tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]   
                file.write(json.dumps(saveable_chain))   
                file.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions] 
                file.write(json.dumps(saveable_tx))
        except (IOError, IndexError):
            print('Saving failed!')


    def proof_of_work(self):
        """Generate a proof of work for the new block that's to be added to the blockchain """
        last_block = self.__chain[-1]                                         
        last_hash = hash_block(last_block)                                        
        proof = 0                                                           
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):         
            proof += 1                                                      
        return proof                                                        


    def get_balance(self):
        """ Subtracts the total amount a participant has sent from the total amount he has received and returns this balance """
        if self.hosting_node == None:   
            return None                 
        
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]    
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]  
        tx_sender.append(open_tx_sender)    

        amount_sent = 0
        for tx in tx_sender:
            if len(tx) > 0:
                amount_sent += sum(tx)

        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        amount_received = 0
        for tx in tx_recipient:
            if len(tx) > 0:
                amount_received += sum(tx)

        return amount_received - amount_sent         


    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """ Store a new transaction in the open transactions (default amount = 1.0) """
        if self.hosting_node == None:   
            return False

        transaction = Transaction(sender, recipient, signature, amount)    
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False


    def mine_block(self): 
        """ Take all the open transactions and add them to a new block. This block gets added to the blockchain. """
        if self.hosting_node == None:   
            return None                 
        
        last_block = self.__chain[-1] 
        hashed_block = hash_block(last_block) 
        
        proof = self.proof_of_work()                 
        
        reward_transaction = Transaction('MINING', self.hosting_node,'', MINING_REWARD)    
        copied_open_transactions = self.__open_transactions[:]     
        
        for tx in copied_open_transactions:         
            if not Wallet.verify_transaction(tx):   
                return None                        
        
        copied_open_transactions.append(reward_transaction) 
        
        block = Block(len(self.__chain), hashed_block, copied_open_transactions, proof)
        self.__chain.append(block)

        self.__open_transactions = []      
        self.save_data()
        return block