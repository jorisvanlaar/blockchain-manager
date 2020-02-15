import hashlib
import json     # geimporteerd omdat je mbv json objecten kunt encoden als een string (wat je wilt voor het encoden van een block naar een string in de hash-function)
from collections import OrderedDict  # geimporteerd om ervoor te zorgen dat al je transaction dictionaries een vaste volgorder/order krijgen

# Initializing global variables
# The reward miners get for creating a new block
MINING_REWARD = 10  # global constant variable

# The starting block for the blockchain
genesis_block = {
        'previous_hash': '',
        'index': 0,
        'transactions': [],
        'proof': 100
    }
# Initializing an empty blockchain list
blockchain = [genesis_block]
# Unhandled transactions
open_transactions = []
owner = 'Joris'
# Myself + other people sending/receiving crypto
participants = {'Joris'}    # Syntax voor een set (stored alleen unieke values, 
                            # Python begrijpt dat het geen dictionary is, want geen key-value pairs)


def hash_block(block):
    """ Hashes a block and returns this hash in the form of a string (thats separated by -'s using list comprehension) """
    # return '-'.join([str(block[key]) for key in block])   # ipv een pseudo-hash in string-vorm, een echte hash gebruiken mbv hashlib
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()       
    # de json.dumps(block).encode() encode een block naar een string
    # het sort_keys=True argument voorkomt dat 
    # de hashlib.sha256() method is een algoritme die een 64-character hash creeert obv een string, en zorgt ervoor dat dezelfde input altijd tot dezelfde hash leidt (wat nodig is om de hash van het vorige block te kunnen validaten)
    # de hexdigest() method convert de 'bytehash' die wordt gegenereerd door sha256() naar een gewone string

    # Zowel een block als een transaction zijn dictionaries. Het probleem van dictionaries is dat ze unordered zijn. 
    # Dit kan betekenen dat de volgorde van de key-value pairs van een block of transaction kan veranderen, 
    # Wat weer kan betekenen dat het hashen van een block verschillende hashes voor dezelfde block kan opleveren, omdat de order van een block en/of transaction kan zijn veranderd.
    # Het gevolg hiervan is dat een correct block bij het checken van de hash alsnog als invalid kan worden gezien.
    # Dit is te fixen met het named argument 'sort_keys' voor de json.dumps() method. Dit zorgt ervoor dat de keys van de dictionary gesorteerd worden voordat deze gedumpt wordt naar een string.
    # Wat betekent dat dezelfde dictionary altijd tot dezelfde string/hash leidt, ook al wijzigt de volgorde van de dictionary.
    # Het vastzetten van de order voor de transaction-dictionaries die je gebruikt in valid_proof() doe je door een OrderedDict te gebruiken ipv een standaard dictionary in add_transaction() en mine_block()
     


def valid_proof(transactions, last_hash, proof):
    """ Generates a hash for a new block and checks whether it fulfills the PoW criteria """
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()  # een lange string maken bestaande uit de transactions, last/previous hash en een 'proof' nummer
    guess_hash = hashlib.sha256(guess).hexdigest()                      # een hash maken van de guess string, hexdigest() om van de hash een weer een leesbare string te maken anders kan je niet checken of ie voldoet
    print(guess_hash)
    return guess_hash[0:2] == '00'                                      # checken of de guess_hash voldoet aan een PoW criterium waarbij de eerste twee karakters van de hash een 0 moeten zijn


def proof_of_work():
    last_block = blockchain[-1]                                         # Verkrijg het huidige laatste block van de chain,
    last_hash = hash_block(last_block)                                  # en hash die.      
    proof = 0                                                           # Initialiseer het proof-nummer op 0
    while not valid_proof(open_transactions, last_hash, proof):         # Met een while-loop checken of valid_proof() op een gegevent moment True returned,
        proof += 1                                                      # door het proof-nummer steeds met 1 te verhogen
    return proof                                                        # En return het proof-nummer dat er voor heeft gezorgd dat aan de PoW criteria is voldaan. 
                                                                        # Dit nummer ga je namelijk toevoegen aan het nieuwe block (bestaande uit de open_transactions) dat aan de chain gaat worden toegevoegd

def get_balance(participant):
    """ Subtracts the total amount a participant has sent from the total amount he has received and returns this balance """

    # Fetch a list of all sent amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of transactions that were already included in blocks of the blockchain
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]    # nested list comprehension die de amount opvraagt van alle transactions van de ingegeven participant, en dit teruggeeft in een list-kopie
    
    # Fetch a list of all sent amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of open transactions (to avoid double spending)
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]  # verzamelt de amounts van een participant die in de open_transactions list staan, in een nieuwe list
    tx_sender.append(open_tx_sender)    # Nu bevat de tx_sender zowel een list van alle transaction-amounts die een participant in de blockchain heeft verstuurd, en een list van alle amounts die de participtant heeft verstuurd en nog in de open_transaction staan.

    amount_sent = 0
    # Calculate the total amount of coins sent
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += sum(tx)
    # Je had ipv de for-loop hierboven ook een reduce function kunnen gebruiken om amount_sent te berekenen
    
    # This fetches received amounts of transactions that were already included in blocks of the blockchain
    # I ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
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
    sender_balance = get_balance(transaction['sender'])
    # if sender_balance >= transaction['amount']:
    #     return True
    # else:
    #     return False
    return sender_balance >= transaction['amount']  # Bovenstaande if/else onnodig, dit returned ook een boolean


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
    # Een OrderedDict is opgebouwd uit een list aan tuples, waarbij elke tuple een key-value pair is.
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
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
    
    # Ook voor de reward_transaction de order vastzetten (net als gewone transaction in add_transaction()) mbv een OrderedDict 
    reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    
    # Copy transaction instead of manipulating the original open_transactions list
    # This ensures that if for some reason the mining should fail, I don't have the reward transaction stored in the open transactions
    copied_open_transactions = open_transactions[:]     # de open_transactons list kopieren dmv slicen, 
    copied_open_transactions.append(reward_transaction) # zodat je voorkomt dat een mislukte transactie toch een reward oplevert voor de miner in de officiele open_transactions list
    
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_open_transactions,
        'proof': proof
    }
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
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):  # Je vergelijkt hier dus of de reeds opgeslagen hash van het voorgaande block ('previous_hash') overeenkomt met de hash die je nu nogmaals laat berekenen/returnen
            print('Previous hash is invalid')
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):  # mbv slicing het laatste element van de transactions (oftewel de reward_transaction) excluden, omdat je die ook niet had meegenomen bij het berekenen van het PoW nummer in mine_block()
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
    print('4: Output participants')
    print('h: Manipulate the chain')
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
    
    elif user_choice == '3':
        print_blockchain_elements()
    
    elif user_choice == '4':
        print(f"Participants: {participants}")
    
    elif user_choice.upper() == 'H':    # Function to manipulate the first block of the chain
        if len(blockchain) >= 1:        # Makes sure that you don't try to "hack" the blockchain if it's empty
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Bas', 'recipient': 'Joris', 'amount': 100.0}]
            }
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
