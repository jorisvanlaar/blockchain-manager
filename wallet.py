from Crypto.PublicKey import RSA    
import Crypto.Random                
import binascii                     
from Crypto.Signature import pkcs1_15   
from Crypto.Hash import SHA256      

class Wallet:
    def __init__(self, node_id):
        self.private_key = None     
        self.public_key = None
        self.node_id = node_id
    

    def create_keys(self):
        """ Creates a private and public key """
        private_key, public_key = self.generate_keys()  
        self.private_key = private_key
        self.public_key = public_key 
        
    
    def save_keys(self):
        """ Saves the public and private key to the wallet.txt file """
        if self.public_key != None and self.private_key != None:
            try:
                with open(f'wallet-{self.node_id}.txt', 'w') as file:       
                    file.write(self.public_key)
                    file.write('\n')
                    file.write(self.private_key)
                return True
            except(IOError, IndexError):
                print('Saving wallet failed')
                return False
        

    def load_keys(self):
        """ Loads the public and private key from the wallet.txt file """
        try:
            with open(f'wallet-{self.node_id}.txt', 'r') as file:           
                keys = file.readlines()             
                public_key = keys[0][:-1]           
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except(IOError, IndexError):
            print('Loading wallet failed')
            return False

    
    def generate_keys(self):
        """ Using PyCryptodome's RSA algorithm to generate a random public and private key """
        private_key = RSA.generate(1024, Crypto.Random.new().read)                                                          
        public_key = private_key.publickey()                                                                                         
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))  

    
    def sign_transaction(self, sender, recipient, amount):
        """ Returns a signature (string) for a given transaction """
        signer = pkcs1_15.new(RSA.importKey(binascii.unhexlify(self.private_key)))   
        tx_hash = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))                
        signature = signer.sign(tx_hash)                                                                
        return binascii.hexlify(signature).decode('ascii')
    

    @staticmethod                                                           
    def verify_transaction(transaction):                                    
        """ Checks whether a signature for a given transaction is valid """
        try:
            public_key = RSA.importKey(binascii.unhexlify(transaction.sender))  
            verifier = pkcs1_15.new(public_key)                                 
            tx_hash = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))     
            signature = binascii.unhexlify(transaction.signature)               

            verification = print(verifier.verify(tx_hash, signature))           
            if verification == None:                                            
                return True                                                     
        except ValueError:                                                      
            return False                                                        
        








