import hashlib
import json
from block import Block
from transaction import Transaction
from helpers.hash_util import hash_block        
from helpers.verification import Verification
from wallet import Wallet
import requests                                     

MINING_REWARD = 10  

class Blockchain:
    def __init__(self, public_key, node_id):        
        genesis_block = Block(0, '', [], 100, 0)    
        self.__chain = [genesis_block]              
        self.__open_transactions = []                                         
        self.public_key = public_key
        self.__peer_nodes = set()           
        self.node_id = node_id
        self.resolve_conflicts = False     
        self.load_data()                  

    
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
    
    
    @property
    def peer_nodes(self):
        return list(self.__peer_nodes)  


    def load_data(self):
        """ Opens the blockchain, open transactions and peer nodes from a file an initializes them """
        try:
            with open(f'blockchain-{self.node_id}.txt', 'r') as file:   
                file_content = file.readlines()                     
                blockchain = json.loads(file_content[0][:-1])       
                updated_blockchain = []
                
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]   
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
            
            open_transactions = json.loads(file_content[1][:-1])     
            updated_transactions = []
            
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])  
                updated_transactions.append(updated_transaction)
            self.__open_transactions = updated_transactions

            peer_nodes = json.loads(file_content[2])
            self.__peer_nodes = set(peer_nodes)

        except (IOError, IndexError):
            print('Could not load data')
    

    def save_data(self):
        """ Stores the blockchain, open transactions and peer nodes in a file """
        try:
            with open(f'blockchain-{self.node_id}.txt', 'w') as file:           
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,[tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]   
                file.write(json.dumps(saveable_chain))   
                file.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions] 
                file.write(json.dumps(saveable_tx))
                file.write('\n')
                file.write(json.dumps(list(self.__peer_nodes))) 
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


    def get_balance(self, sender=None): 
        """ Subtracts the total amount a participant has sent from the total amount he has received and returns this balance """
        if sender == None:                  
            if self.public_key == None:   
                return None
            participant = self.public_key   
        else:                                
            participant = sender            

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


    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """ Add a new transaction to the open transactions """
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            # Broadcast new transaction to peer nodes
            if not is_receiving:                                            
                for node in self.__peer_nodes:                              
                    url = f'http://{node}/broadcast-transaction'            
                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:      
                            print('Transaction declined, needs resolving')
                            return False                                                    
                    except requests.exceptions.ConnectionError:                             
                        continue                                                            
            return True
        return False


    def mine_block(self): 
        """ Take all the open transactions and add them to a new block. This block gets added to the blockchain. """
        if self.public_key == None:   
            return None                 
        
        last_block = self.__chain[-1] 
        hashed_block = hash_block(last_block) 
        
        proof = self.proof_of_work()                 
        
        reward_transaction = Transaction('MINING', self.public_key,'', MINING_REWARD)    
        copied_open_transactions = self.__open_transactions[:]     
        
        for tx in copied_open_transactions:         
            if not Wallet.verify_transaction(tx):   
                return None                        
        
        copied_open_transactions.append(reward_transaction) 
        
        block = Block(len(self.__chain), hashed_block, copied_open_transactions, proof)
        self.__chain.append(block)

        self.__open_transactions = []      
        self.save_data()
        # Broadcast new block to peer nodes
        for node in self.__peer_nodes:                  
            url = f'http://{node}/broadcast-block'      
            converted_block = block.__dict__.copy()     
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]   
            try:        
                response = requests.post(url,json={'block': converted_block})   
                if response.status_code == 400 or response.status_code == 500:      
                    print('Block declined, needs resolving')
                if response.status_code == 409:                  
                    self.resolve_conflicts = True               
            except requests.exceptions.ConnectionError:                         
                continue                                                        
        return block
    

    def add_block(self, block):
        """ Adding block to blockchain functionality meant for peer nodes that verify a new block. This way all nodes keep their version of the blockchain up to date """
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]       
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])                            
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        
        if not proof_is_valid or not hashes_match:      
            return False                                
        
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])       
        self.__chain.append(converted_block)
        
        stored_transactions = self.__open_transactions[:]   
        for incoming_tx in block['transactions']:           
            for open_tx in stored_transactions:             
                if open_tx.sender == incoming_tx['sender'] and open_tx.recipient == incoming_tx['recipient'] and open_tx.amount == incoming_tx['amount'] and open_tx.signature == incoming_tx['signature']:
                    try:
                        self.__open_transactions.remove(open_tx)    
                    except ValueError:                              
                        print('Item was already removed')
        self.save_data()
        return True
    

    def resolve(self):
        winner_chain = self.chain               
        replace = False                         

        for node in self.__peer_nodes:          
            url = f'http://{node}/chain'    
            try:
                response = requests.get(url)    
                peer_node_chain = response.json()                                                                                                                             
                peer_node_chain = [Block(block['index'], block['previous_hash'], [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']], block['proof'], block['timestamp'] ) for block in peer_node_chain]  

                peer_node_chain_length = len(peer_node_chain)
                local_node_chain_length = len(winner_chain)

                if peer_node_chain_length > local_node_chain_length and Verification.verify_chain(peer_node_chain):     
                    winner_chain = peer_node_chain                                                                      
                    replace = True                                                                                      
            except requests.exceptions.ConnectionError:     
                continue                                    
        
        self.resolve_conflicts = False          
        self.chain = winner_chain               

        if replace:                         
            self.__open_transactions = []   
        self.save_data()                    
        return replace                      


    def add_peer_node(self, node):
        """ Adds a new node to the peer_nodes set 
        
        Arguments:
            :node: The node URL (IP address/port) which should be added
        """
        self.__peer_nodes.add(node)
        self.save_data()           
    

    def remove_peer_node(self, node):
        """ Removes a node from the peer_nodes set 
        
        Arguments:
        :node: The node URL (IP address/port) which should be removed
        """
        self.__peer_nodes.discard(node)
        self.save_data()


