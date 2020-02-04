# Initializing global variables
genesis_block = {
        'previous_hash': '',
        'index': 0,
        'transactions': []
    }
blockchain = [genesis_block]
open_transactions = []
owner = 'Joris'


def hash_block(block):
    """ Returns a hash in the form of a string (thats separated by -'s using list comprehension) """
    return '-'.join([str(block[key]) for key in block]) 



def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Store a new transaction in the open transactions 
    
    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount of coins sent with the transaction (default = 1.0)
    """
    transaction = {
        'sender': sender, 
        'recipient': recipient, 
        'amount': amount
    }
    open_transactions.append(transaction)


def mine_block():
    """ Take all the open transactions and add them to a new block. This block gets added to the blockchain. """
    last_block = blockchain[-1] # This would throw an error for the very first block, since the blockchain is then empty. So we need a genesis block (see line 2).
    hashed_block = hash_block(last_block) 
    
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }
    blockchain.append(block)


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
        print(block)
    else:               # Get executed when the loop is done
        print('-' * 20)


def verify_chain():
    """ Compares the stored 'previous_hash' in a block with a recalculated hash """
    for (index, block) in enumerate(blockchain): # if you wrap a list with the helper function 'enumerate', it will give you back a tuple consisting of the index & value of an element
                                                 # In this case we immediately unpack the tuple values to the variables 'index' and 'block'
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):  # Je vergelijkt hier dus of de reeds opgeslagen hash van het voorgaande block (in 'previous_hash') overeenkomt met de hash die je nu nogmaals laat berekenen/returnen
            return False
    return True


menu = True

while menu:
    print('Please choose:')
    print('1: Add a new transaction')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('h: Manipulate the chain')
    print('q: Quit')

    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_values()  
        recipient, amount = tx_data         # unpacken van de tuple 'tx_data' en diens values in de variabelen 'recipient' en 'amount' stoppen
        # Add the transaction to the open_transactions list
        add_transaction(recipient, amount=amount) # kwarg zodat het tweede argument niet voor de 'sender' parameter wordt gebruikt (die gebruikt dan de default 'owner' variabele)
        print(open_transactions)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice.upper() == 'H':    # Function to manipulate the first block of the chain into a value of 2
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Bas', 'recipient': 'Joris', 'amount': 100.0}]
            }
    elif user_choice.upper() == 'Q':
        # break
        menu = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():              # if verify_chain() returns False -> print a message
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
# gets executed when the loop is done (doesn't work when you break out of the loop)
else:
    print('User left')

print('Done!')
