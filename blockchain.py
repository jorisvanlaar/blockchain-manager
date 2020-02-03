# Initializing global variables
blockchain = []
open_transactions = []
owner = 'Joris'


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
    """ Add a new block to the blockchain, containing the open transactions """
    pass


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
    """ Verifies whether the first element of the current block is equal to the complete previous block. """
    is_valid = True

    for block_index in range(len(blockchain)):
        if block_index == 0:
            continue
        elif blockchain[block_index][0] == blockchain[block_index - 1]:
            is_valid = True
        else:
            is_valid = False
            break
    return is_valid


menu = True

while menu:
    print('Please choose:')
    print('1: Add a new transaction value')
    print('2: Output the blockchain blocks')
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
        print_blockchain_elements()
    elif user_choice.upper() == 'H':    # Function to manipulate the first block of the chain into a value of 2
        if len(blockchain) >= 1:
            blockchain[0] = [2]
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
