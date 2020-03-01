from hash_util import hash_string_256, hash_block

class Verification:
    def valid_proof(self, transactions, last_hash, proof):
        """ Generates a guess-hash for a new block, and checks whether it fulfills the PoW criteria """
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()  # een lange string maken obv de transactions, last/previous hash en een 'proof' nummer. En mbv list comprehension en de to_ordered_dict() method (van de Transaction class) alle Transaction objecten converten naar een OrderedDict om zo de order te waarborgen van de transactions
        guess_hash = hash_string_256(guess)                                 # een hash maken van de guess string. # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm. 
        return guess_hash[0:2] == '00'                                      # checken of de guess_hash voldoet aan een PoW criterium waarbij de eerste twee karakters van de hash een 0 moeten zijn


    def verify_chain(self, blockchain):
        """ Compares the stored 'previous_hash' in a block with a recalculation of the hash which you do here """
        for (index, block) in enumerate(blockchain): # if you wrap a list with the helper function 'enumerate', it will give you back a tuple consisting of the index & value of an element
                                                    # In this case I immediately unpack the tuple values to the variables 'index' and 'block'
            if index == 0:                           # skip the genesis block
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):  # Je vergelijkt hier dus of de reeds opgeslagen hash van het voorgaande block ('previous_hash') overeenkomt met de hash die je nu nogmaals laat berekenen/returnen
                print('Previous hash is invalid')
                return False
            if not self.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):  # mbv slicing het laatste element van de transactions (oftewel de reward_transaction) excluden, omdat je die ook niet had meegenomen bij het berekenen van het PoW nummer in mine_block()
                print('Proof of Work is invalid')
                return False
        return True
    

    def verify_transaction(self, transaction, get_balance):
        """ Verifies whether the sender has enough funds to send a transaction """
        sender_balance = get_balance(transaction.sender)
        # if sender_balance >= transaction['amount']:
        #     return True
        # else:
        #     return False
        return sender_balance >= transaction.amount  # Bovenstaande if/else onnodig, dit returned ook een boolean