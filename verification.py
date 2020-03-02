from hash_util import hash_string_256, hash_block

class Verification:
    # Zowel met staticmethods als classmethods zorg je ervoor dat je niet eerst een instance van een Class moet aanmaken waarop je de methods van de Class kunt callen. 
    # Maar kun je direct op de Class zelf diens methods callen. In dit geval zou je dus direct Verification.valid_proof() kunnen gebruiken om deze static method te callen.
    # Het verschil tussen classmethods en staticmethods, is dat je bij classmethods nog wel toegang hebt tot de class attributes en methods in de class (mbv het 'cls' argument), 
    # staticmethods hebben die toegang niet. Dat zijn eigenlijk gewoon puur methods die compleet zijn losgekoppeld van de Class.
    # Staticmethods worden vooral gebruikt om een groepering van methods duidelijk te maken.  
    # Voordeel hiervan is dat je in node.py en blockchain.py nu niet meer eerst een instance van de Verification class hoeft aan te maken voor toegang tot de methods van deze Class, wat logischer is voor een helper class.
    @staticmethod   
    def valid_proof(transactions, last_hash, proof):    # heeft dus als static method ook niet meer het self-argument nodig
        """ Generates a guess-hash for a new block, and checks whether it fulfills the PoW criteria """
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()  # een lange string maken obv de transactions, last/previous hash en een 'proof' nummer. En mbv list comprehension en de to_ordered_dict() method (van de Transaction class) alle Transaction objecten converten naar een OrderedDict om zo de order te waarborgen van de transactions
        guess_hash = hash_string_256(guess)                                 # een hash maken van de guess string. # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm. 
        return guess_hash[0:2] == '00'                                      # checken of de guess_hash voldoet aan een PoW criterium waarbij de eerste twee karakters van de hash een 0 moeten zijn


    @classmethod
    def verify_chain(cls, blockchain):          # cls ipv self argument
        """ Compares the stored 'previous_hash' in a block with a recalculation of the hash which you do here """
        for (index, block) in enumerate(blockchain): # if you wrap a list with the helper function 'enumerate', it will give you back a tuple consisting of the index & value of an element
                                                    # In this case I immediately unpack the tuple values to the variables 'index' and 'block'
            if index == 0:                           # skip the genesis block
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):  # Je vergelijkt hier dus of de reeds opgeslagen hash van het voorgaande block ('previous_hash') overeenkomt met de hash die je nu nogmaals laat berekenen/returnen
                print('Previous hash is invalid')
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):  # mbv slicing het laatste element van de transactions (oftewel de reward_transaction) excluden, omdat je die ook niet had meegenomen bij het berekenen van het PoW nummer in mine_block()
                print('Proof of Work is invalid')
                return False
        return True
    

    @staticmethod
    def verify_transaction(transaction, get_balance):
        """ Verifies whether the sender has enough funds to send a transaction """
        sender_balance = get_balance()
        # if sender_balance >= transaction['amount']:
        #     return True
        # else:
        #     return False
        return sender_balance >= transaction.amount  # Bovenstaande if/else onnodig, dit returned ook een boolean