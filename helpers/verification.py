from helpers.hash_util import hash_block, hash_string_256
from wallet import Wallet 

class Verification:
    @staticmethod   
    def valid_proof(transactions, last_hash, proof):
        """ Generates a guess-hash for a new block, and checks whether it fulfills the PoW criteria """
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)                                  
        return guess_hash[0:2] == '00'


    @classmethod
    def verify_chain(cls, blockchain):          
        """ Verifies the proof of work and compares the stored 'previous_hash' with a recalculated hash that you do here """
        for (index, block) in enumerate(blockchain): 
            if index == 0:                           
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                print('Previous hash is invalid')
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):  
                print('Proof of Work is invalid')
                return False
        return True
    

    @staticmethod
    def verify_transaction(transaction, get_balance):    
        """ Verifies whether the sender has enough funds and a valid signature for a given transaction """                     
        sender_balance = get_balance(transaction.sender)    
        return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)

