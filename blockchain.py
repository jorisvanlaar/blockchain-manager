import hashlib
from hash_util import hash_block
import json
from block import Block
from transaction import Transaction
from verification import Verification

# Initializing global variables
# The reward miners get for creating a new block
MINING_REWARD = 10  # global constant variable

class Blockchain:
    def __init__(self, hosting_node_id):    
        genesis_block = Block(0, '', [], 100, 0)    # The starting block for the blockchain
        self.__chain = [genesis_block]              # Initializing an empty blockchain list with a genesis block, but this will be overwritten when data is loaded in. private gemaakt zodat die niet makkelijk van buiten deze class gewijzigd kan worden
        self.__open_transactions = []               # Unhandled transactions, private gemaakt zodat die niet makkelijk van buiten deze class gewijzigd kan worden
        self.load_data()                            # load_data() uitvoeren op het moment dat er een Blockchain object wordt aangemaakt
        self.hosting_node = hosting_node_id         # id voor de computer waarop de instance van de Blockchain draait

    
    # getter maken om het private attribute __chain te kunnen benaderen van buiten de class
    # def get_chain(self):
    #     return self.__chain[:]  # mbv slicing een kopie returnen, en niet de originele chain die in de Blockchain instance wordt bewaard (voor de zekerheid)
     
    # Maar ipv bovenstaande get_chain getter kun je ook een propery aanmaken die als getter fungeert, maar een fijnere syntax geeft
    @property
    def chain(self):
        return self.__chain[:]  # mbv slicing een kopie returnen, en niet de originele chain die in de Blockchain instance wordt bewaard (voor de zekerheid)
    
    # Setter aanmaken voor de private attribute __chain
    @chain.setter
    def chain(self, value):
        self.__chain = value
    

    # # getter maken om het private attribute __open_transactions te kunnen benaderen van buiten de class
    # def get_open_transactions(self):
    #     return self.__open_transactions[:]  # mbv slicing een kopie returnen, en niet de originele chain die in de Blockchain instance wordt bewaard (voor de zekerheid)

    @property
    def open_transactions(self):
        return self.__open_transactions[:]  # mbv slicing een kopie returnen, en niet de originele chain die in de Blockchain instance wordt bewaard (voor de zekerheid)

    @open_transactions.setter
    def open_transactions(self, value):
        self.__open_transactions = value


    def load_data(self):
        """ Opens the blockchain & open transactions from a file an initializes the blockchain and open transactions """
        try:
            with open('blockchain.txt', 'r') as file:
                file_content = file.readlines()                     # readlines() returns a list with the content of the file that's being read
                blockchain = json.loads(file_content[0][:-1])       # deserialiseren van de opgeslagen json-data terug naar een Python list. En mbv slicing het laatste karakter ('/n') excluden
                
                # De blockchain wordt als invalid gezien op het moment dat je de data inlaad en de transactions van een block niet meer een OrderedDict zijn (terwijl je de transactions wel als OrderedDict in add_transaction() had toegevoegd). 
                # Deze OrderedDict informatie gaat namelijk verloren tijdens het wegschrijven van JSON data naar de schijf.
                # Er is dus een verschil ontstaan tussen de oorspronkelijke blockchain data en de blockchain data die je inlaadt. 
                # Dit voorkom je door met een for-loop door de ingeladen blockchain te gaan (previous_hash, index, proof laat je ongewijzigd),
                # en de transactions te overwriten (mbv een list comprehension) en elk block te converten naar een OrderedDict.
                updated_blockchain = []
                for block in blockchain:
                    # converted_tx = [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]  # de ingeladen transactions converten naar een OrderedDict mbv een list comprehension
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]   # de ingeladen transaction mbv list comprehension converten naar een list aan Transactions, ipv OrderedDicts zoals de line hierboven
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
            
            # Ook voor de open_transactions geldt dat die nu niet worden ingeladen als een OrderedDict wat resulteert in een invalid blockchain,
            # dus die moet ook bij het inladen omgezet worden naar een OrderedDict:
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                # updated_transaction = OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])  # De ingeladen open_transactions converten naar Transaction objecten (ipv OrderedDict zoals de line hierboven) en appenden aan de updated_transactions list
                updated_transactions.append(updated_transaction)
            self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            print('Could not load data')
    

    def save_data(self):
        """ Stores the blockchain and open transactions in a file """
        try:
            with open('blockchain.txt', 'w') as file:
                # Objecten kunnen niet als json worden opgeslagen, en aangezien de blockchain een list aan Blocks (oftewel objecten) is, 
                # moet je die eerst converten naar een list aan bijv. dictionaries
                # Maar __dict__ convert alleen het overkoepelende object, niet ook geneste lists aan objecten BINNEN dat overkoepelende object.
                # Daarvoor gebruik je een nested list comprehension om de transactions binnen een Block object ook te converten naar dictionaries
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,[tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]   
                
                file.write(json.dumps(saveable_chain))  # json.dumps() zorgt ervoor dat de blockchain-list wordt geconvert naar json-data (een json-string). Want als je een list als een normale string opslaat in een .txt bestand, krijg je die niet meer terug-geconvert naar een list bij het inladen. Dat kan met json-data die je opslaat in een .txt wel. 
                file.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions] # Objecten kunnen niet als json worden opgeslagen, en aangezien de open_transactions een list aan Transaction objecten is, moet je die eerst converten naar een list aan bijv. dictionaries (want dat datatype is wel weg te schrijven naar JSON)
                file.write(json.dumps(saveable_tx))
        except (IOError, IndexError):
            print('Saving failed!')


    def proof_of_work(self):
        """Generate a proof of work for the new block that's to be added to the blockchain """
        last_block = self.__chain[-1]                                         # Verkrijg het huidige laatste block van de chain,
        last_hash = hash_block(last_block)                                  # en hash die, zodat je de previous_hash/last_hash hebt.      
        proof = 0                                                           # Initialiseer het proof-nummer op 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):         # Met een while-loop checken of valid_proof() op een gegevent moment True returned,
            proof += 1                                                      # door het proof-nummer steeds met 1 te verhogen
        return proof                                                        # En return het proof-nummer dat er voor heeft gezorgd dat aan de PoW criteria is voldaan. 
                                                                            # Dit nummer ga je namelijk toevoegen aan het nieuwe block (opgebouwd uit de huidige open_transactions) dat aan de chain gaat worden toegevoegd

    def get_balance(self):
        """ Subtracts the total amount a participant has sent from the total amount he has received and returns this balance """
        participant = self.hosting_node

        # Fetch a list of all sent amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of transactions that were already included in blocks of the blockchain
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]    # nested list comprehension die de amount opvraagt van alle transactions van de ingegeven participant, en dit teruggeeft in een list-kopie
        
        # Fetch a list of all sent amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of open transactions (to avoid double spending)
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]  # verzamelt de amounts van een participant die in de open_transactions list staan, in een nieuwe list
        tx_sender.append(open_tx_sender)    # Nu bevat de tx_sender zowel een list van alle transaction-amounts die een participant in de blockchain heeft verstuurd, en een list van alle amounts die de participtant heeft verstuurd en nog in de open_transaction staan.

        amount_sent = 0
        # Calculate the total amount of coins sent
        for tx in tx_sender:
            if len(tx) > 0:
                amount_sent += sum(tx)
        # Je had ipv de for-loop hierboven ook een reduce function kunnen gebruiken om amount_sent te berekenen
        
        # This fetches received amounts of transactions that were already included in blocks of the blockchain
        # I ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        amount_received = 0
        for tx in tx_recipient:
            if len(tx) > 0:
                amount_received += sum(tx)
        # Je had ipv de for-loop hierboven ook een reduce function kunnen gebruiken om amount_received te berekenen 

        # Return the total balance
        return amount_received - amount_sent         


    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, amount=1.0):
        """ Store a new transaction in the open transactions 
        
        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount of coins sent with the transaction (default = 1.0)
        """
        # transaction = {
        #     'sender': sender, 
        #     'recipient': recipient, 
        #     'amount': amount
        # }

        # ipv (zoals bovenstaand) een transaction in de vorm van een standaard dictionary aan te maken, 
        # ga je dat doen met een OrderedDict. Om ervoor te zorgen dat de order van je transactions altijd vaststaat. 
        # Dit is nodig zodat je dan altijd dezelfde correcte hash genereert voor eenzelfde block in de valid_proof() method
        # Een OrderedDict is opgebouwd uit een list aan tuples, waarbij elke tuple een key-value pair is:
        # transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
        transaction = Transaction(sender, recipient, amount)    # niet een OrderedDict (zoals line hierboven), maar een Transaction object aanmaken
        if Verification.verify_transaction(transaction, self.get_balance):  # Notice het ontbreken van haakjes, omdat je niet de get_balance() called maar puur een reference ernaartoe passed als argument 
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False


    def mine_block(self): #  The node parameter stands for the computer that is mining the block
        """ Take all the open transactions and add them to a new block. This block gets added to the blockchain. """
        # Fetch the currently last block of the blockchain
        last_block = self.__chain[-1] # This would throw an error for the very first block, since the blockchain is then empty. So I need a genesis block for the blockchain to prevent this.
        # Hash the last block of the chain (to be able to compare it in the verify_chain() method)
        hashed_block = hash_block(last_block) 
        # print(f"Hash current last block in the blockchain: {hashed_block}")
        
        proof = self.proof_of_work()                 # laat een geldig PoW nummer genereren
        
        # extra transaction that rewards the miner
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,
        #     'amount': MINING_REWARD
        # }
        # Ook voor de reward_transaction de order vastzetten (net als gewone transactions in add_transaction()) mbv een OrderedDict 
        # reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)    # ipv een OrderedDict ook voor de reward_transaction een Transaction object aanmaken 
        
        # Copy transaction instead of manipulating the original open_transactions list
        # This ensures that if for some reason the mining should fail, I don't have the reward transaction stored in the open transactions
        copied_open_transactions = self.__open_transactions[:]     # de open_transactons list kopieren dmv slicen, 
        copied_open_transactions.append(reward_transaction) # zodat je voorkomt dat een mislukte transactie toch een reward oplevert voor de miner in de officiele open_transactions list
        
        block = Block(len(self.__chain), hashed_block, copied_open_transactions, proof)
        self.__chain.append(block)

        self.__open_transactions = []      # reset/leeg de open_transaction na het toevoegen van het nieuwe block aan de blockchain
        self.save_data()
        return True