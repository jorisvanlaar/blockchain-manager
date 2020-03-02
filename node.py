from uuid import uuid4                  # Importeren Uniform Unique ID package, en dan specifiek het uuid4 algoritme voor het genereren van een uniek id
from blockchain import Blockchain
from verification import Verification


class Node:
    def __init__(self):
        # self.id = str(uuid4())                       # het uuid4 algoritme direct laten uitvoeren bij de aanmaak van een Node instance, om deze zijn eigen hosting_node_id mee te geven. Wel wrappen in een str(), omdat een UUID object niet json serializable is, wat dus issues anders geeft met saven/loaden
        self.id = 'JORIS'                               
        self.blockchain = Blockchain(self.id)   
        

    def get_transaction_values(self):
        """ Returns the input of the user (a new transaction amount) as a float. """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount: '))
        return tx_recipient, tx_amount


    def get_user_choice(self):
        """ Prompts the user for a choice and returns it. """
        user_input = input('Your choice: ')
        return user_input


    def print_blockchain_elements(self):
        """ Outputs all blocks of the blockchain """
        for block in self.blockchain.chain:
            print(f"Block: {block}")
        else:               # Gets executed when the loop is done
            print('-' * 20)
    

    def listen_for_input(self):
        # A while loop for the user input interface
        # It's a loop that exits once menu becomes False or when break is called
        menu = True
        
        while menu:
            print('Please choose:')
            print('1: Add a new transaction')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('q: Quit')

            user_choice = self.get_user_choice()
            
            if user_choice == '1':
                tx_data = self.get_transaction_values()  
                recipient, amount = tx_data         # unpacken van de tuple 'tx_data' en diens values in de variabelen 'recipient' en 'amount' stoppen
                # Add the transaction to the open_transactions list
                if self.blockchain.add_transaction(recipient, self.id, amount=amount): # kwarg zodat het tweede argument niet voor de 'sender' parameter wordt gebruikt (die gebruikt dan de default 'owner' variabele)
                    print('Added transaction!')
                else:
                    print('Transaction failed, insufficient funds!')
                print(f"Open transactions: {self.blockchain.open_transactions}")
            
            elif user_choice == '2':
                self.blockchain.mine_block()
            
            elif user_choice == '3':
                self.print_blockchain_elements()
            
            elif user_choice.upper() == 'Q':
                # break
                menu = False        # This will lead to the loop to exit because it's running condition becomes False
            
            else:
                print('Input was invalid, please pick a value from the list!')
            
            verifier = Verification()                               # Een instance van de Verification class aanmaken, zodat je toegang hebt tot diens methods
            if not verifier.verify_chain(self.blockchain.chain):    # if verify_chain() returns False -> print a message
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break                           # Break out of the loop

            print(f"Balance of {self.id}: {self.blockchain.get_balance():.2f}")         # Pas als je de open transactions hebt gemined wordt de nieuwe balance van de node getoond. Note dat je de float limit tot maar 2 decimalen.

        # gets executed when the loop is done (doesn't work when you break out of the loop)
        else:
            print('User left')

        print('Done!')


node = Node()
node.listen_for_input()