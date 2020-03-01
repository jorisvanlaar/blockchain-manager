import hashlib
from hash_util import hash_string_256, hash_block
import json
from block import Block
from transaction import Transaction

# Initializing global variables
# The reward miners get for creating a new block
MINING_REWARD = 10  # global constant variable

# Initializing an empty blockchain list
blockchain = []
# Unhandled transactions
open_transactions = []
owner = 'Joris'


def load_data():
    """ Opens the blockchain & open transactions from a file an initializes the blockchain and open transactions """
    global blockchain
    global open_transactions

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
            blockchain = updated_blockchain
        
        # Ook voor de open_transactions geldt dat die nu niet worden ingeladen als een OrderedDict wat resulteert in een invalid blockchain,
        # dus die moet ook bij het inladen omgezet worden naar een OrderedDict:
        open_transactions = json.loads(file_content[1])
        updated_transactions = []
        for tx in open_transactions:
            # updated_transaction = OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
            updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])  # De ingeladen open_transactions converten naar Transaction objecten (ipv OrderedDict zoals de line hierboven) en appenden aan de updated_transactions list
            updated_transactions.append(updated_transaction)
        open_transactions = updated_transactions
    except (IOError, IndexError):
        # print('File not found!')
        
        # Wanneer er geen blockchain.txt bestaat, initialiseer dan de blockchain met een genesis block
        # The starting block for the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]    # Initializing an empty blockchain list
        open_transactions = []          # Unhandled transactions
    


load_data()             # load_data() uitvoeren als je blockchain.py runned


def save_data():
    """ Stores the blockchain and open transactions in a file """
    try:
        with open('blockchain.txt', 'w') as file:
            # Objecten kunnen niet als json worden opgeslagen, en aangezien de blockchain een list aan Blocks (oftewel objecten) is, 
            # moet je die eerst converten naar een list aan bijv. dictionaries
            # Maar __dict__ convert alleen het overkoepelende object, niet ook geneste lists aan objecten BINNEN dat overkoepelende object.
            # Daarvoor gebruik je een nested list comprehension om de transactions binnen een Block object ook te converten naar dictionaries
            saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,[tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in blockchain]]   
            
            file.write(json.dumps(saveable_chain))  # json.dumps() zorgt ervoor dat de blockchain-list wordt geconvert naar json-data (een json-string). Want als je een list als een normale string opslaat in een .txt bestand, krijg je die niet meer terug-geconvert naar een list bij het inladen. Dat kan met json-data die je opslaat in een .txt wel. 
            file.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions] # Objecten kunnen niet als json worden opgeslagen, en aangezien de open_transactions een list aan Transaction objecten is, moet je die eerst converten naar een list aan bijv. dictionaries (want dat datatype is wel weg te schrijven naar JSON)
            file.write(json.dumps(saveable_tx))
    except (IOError, IndexError):
        print('Saving failed!')


def valid_proof(transactions, last_hash, proof):
    """ Generates a guess-hash for a new block, and checks whether it fulfills the PoW criteria """
    guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()  # een lange string maken obv de transactions, last/previous hash en een 'proof' nummer. En mbv list comprehension en de to_ordered_dict() method (van de Transaction class) alle Transaction objecten converten naar een OrderedDict om zo de order te waarborgen van de transactions
    guess_hash = hash_string_256(guess)                                 # een hash maken van de guess string. # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm. 
    return guess_hash[0:2] == '00'                                      # checken of de guess_hash voldoet aan een PoW criterium waarbij de eerste twee karakters van de hash een 0 moeten zijn


def proof_of_work():
    """Generate a proof of work for the new block that's to be added to the blockchain """
    last_block = blockchain[-1]                                         # Verkrijg het huidige laatste block van de chain,
    last_hash = hash_block(last_block)                                  # en hash die, zodat je de previous_hash/last_hash hebt.      
    proof = 0                                                           # Initialiseer het proof-nummer op 0
    while not valid_proof(open_transactions, last_hash, proof):         # Met een while-loop checken of valid_proof() op een gegevent moment True returned,
        proof += 1                                                      # door het proof-nummer steeds met 1 te verhogen
    return proof                                                        # En return het proof-nummer dat er voor heeft gezorgd dat aan de PoW criteria is voldaan. 
                                                                        # Dit nummer ga je namelijk toevoegen aan het nieuwe block (opgebouwd uit de huidige open_transactions) dat aan de chain gaat worden toegevoegd

def get_balance(participant):
    """ Subtracts the total amount a participant has sent from the total amount he has received and returns this balance """

    # Fetch a list of all sent amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of transactions that were already included in blocks of the blockchain
    tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in blockchain]    # nested list comprehension die de amount opvraagt van alle transactions van de ingegeven participant, en dit teruggeeft in een list-kopie
    
    # Fetch a list of all sent amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of open transactions (to avoid double spending)
    open_tx_sender = [tx.amount for tx in open_transactions if tx.sender == participant]  # verzamelt de amounts van een participant die in de open_transactions list staan, in een nieuwe list
    tx_sender.append(open_tx_sender)    # Nu bevat de tx_sender zowel een list van alle transaction-amounts die een participant in de blockchain heeft verstuurd, en een list van alle amounts die de participtant heeft verstuurd en nog in de open_transaction staan.

    amount_sent = 0
    # Calculate the total amount of coins sent
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += sum(tx)
    # Je had ipv de for-loop hierboven ook een reduce function kunnen gebruiken om amount_sent te berekenen
    
    # This fetches received amounts of transactions that were already included in blocks of the blockchain
    # I ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
    tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in blockchain]
    amount_received = 0
    for tx in tx_recipient:
        if len(tx) > 0:
            amount_received += sum(tx)
    # Je had ipv de for-loop hierboven ook een reduce function kunnen gebruiken om amount_received te berekenen 

    # Return the total balance
    return amount_received - amount_sent         


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    """ Verifies whether the sender has enough funds to send a transaction """
    sender_balance = get_balance(transaction.sender)
    # if sender_balance >= transaction['amount']:
    #     return True
    # else:
    #     return False
    return sender_balance >= transaction.amount  # Bovenstaande if/else onnodig, dit returned ook een boolean


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Store a new transaction in the open transactions 
    
    Arguments:
        :sender: The sender of the coins (default = owner).
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
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


def mine_block():
    """ Take all the open transactions and add them to a new block. This block gets added to the blockchain. """
    # Fetch the currently last block of the blockchain
    last_block = blockchain[-1] # This would throw an error for the very first block, since the blockchain is then empty. So I need a genesis block for the blockchain to prevent this.
    # Hash the last block of the chain (to be able to compare it in the verify_chain() method)
    hashed_block = hash_block(last_block) 
    # print(f"Hash current last block in the blockchain: {hashed_block}")
    
    proof = proof_of_work()                 # laat een geldig PoW nummer genereren
    
    # extra transaction that rewards the miner
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    # Ook voor de reward_transaction de order vastzetten (net als gewone transactions in add_transaction()) mbv een OrderedDict 
    # reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)    # ipv een OrderedDict ook voor de reward_transaction een Transaction object aanmaken 
    
    # Copy transaction instead of manipulating the original open_transactions list
    # This ensures that if for some reason the mining should fail, I don't have the reward transaction stored in the open transactions
    copied_open_transactions = open_transactions[:]     # de open_transactons list kopieren dmv slicen, 
    copied_open_transactions.append(reward_transaction) # zodat je voorkomt dat een mislukte transactie toch een reward oplevert voor de miner in de officiele open_transactions list
    
    block = Block(len(blockchain), hashed_block, copied_open_transactions, proof)
    blockchain.append(block)
    return True


def get_transaction_values():
    """ Returns the input of the user (a new transaction amount) as a float. """
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount: '))
    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    for block in blockchain:
        print(f"Block: {block}")
    else:               # Gets executed when the loop is done
        print('-' * 20)


def verify_chain():
    """ Compares the stored 'previous_hash' in a block with a recalculation of the hash which you do here """
    for (index, block) in enumerate(blockchain): # if you wrap a list with the helper function 'enumerate', it will give you back a tuple consisting of the index & value of an element
                                                 # In this case I immediately unpack the tuple values to the variables 'index' and 'block'
        if index == 0:                           # skip the genesis block
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):  # Je vergelijkt hier dus of de reeds opgeslagen hash van het voorgaande block ('previous_hash') overeenkomt met de hash die je nu nogmaals laat berekenen/returnen
            print('Previous hash is invalid')
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):  # mbv slicing het laatste element van de transactions (oftewel de reward_transaction) excluden, omdat je die ook niet had meegenomen bij het berekenen van het PoW nummer in mine_block()
            print('Proof of Work is invalid')
            return False
    return True


menu = True
# A while loop for the user input interface
# It's a loop that exits once waiting_for_input becomes False or when break is called
while menu:
    print('Please choose:')
    print('1: Add a new transaction')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('q: Quit')

    user_choice = get_user_choice()
    
    if user_choice == '1':
        tx_data = get_transaction_values()  
        recipient, amount = tx_data         # unpacken van de tuple 'tx_data' en diens values in de variabelen 'recipient' en 'amount' stoppen
        # Add the transaction to the open_transactions list
        if add_transaction(recipient, amount=amount): # kwarg zodat het tweede argument niet voor de 'sender' parameter wordt gebruikt (die gebruikt dan de default 'owner' variabele)
            print('Added transaction!')
        else:
            print('Transaction failed, insufficient funds!')
        print(f"Open transactions: {open_transactions}")
    
    elif user_choice == '2':
        if mine_block():                # Als mine_block() True returned,
            open_transactions = []      # leeg dan de open_transactions
            save_data()
    
    elif user_choice == '3':
        print_blockchain_elements()
    
    elif user_choice.upper() == 'Q':
        # break
        menu = False        # This will lead to the loop to exit because it's running condition becomes False
    
    else:
        print('Input was invalid, please pick a value from the list!')
    
    if not verify_chain():              # if verify_chain() returns False -> print a message
        print_blockchain_elements()
        print('Invalid blockchain!')
        break                           # Break out of the loop

    print(f"Balance: {get_balance('Joris'):.2f}")         # Pas als je de open transactions hebt gemined wordt de nieuwe balance van Joris getoond. Note dat je de float limit tot maar 2 decimalen.

# gets executed when the loop is done (doesn't work when you break out of the loop)
else:
    print('User left')

print('Done!')
