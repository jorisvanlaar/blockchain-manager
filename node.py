from uuid import uuid4                  # Importeren Uniform Unique ID package, en dan specifiek het uuid4 algoritme voor het genereren van een uniek id
from blockchain import Blockchain
from helpers.verification import Verification
from wallet import Wallet


class Node:
    def __init__(self):
        # self.id = str(uuid4())    # het uuid4 algoritme direct laten uitvoeren bij de aanmaak van een Node instance, om deze zijn eigen hosting_node_id mee te geven. Wel wrappen in een str(), omdat een UUID object niet json serializable is, wat dus issues anders geeft met saven/loaden
        self.wallet = Wallet()      # Bij het aanmaken van een Node object, wordt direct een Wallet object aangemaakt, waarbij de keys nog op None staan                    
        # self.blockchain = None      # De blockchain eerst op None initialiseren, omdat je die pas wilt instantieren met een Blockchain object op het moment dat je een public key hebt die niet None is. En dat gebeurt bij menu-optie 4 of 5 
        # Workaround voor line hierboven om te voorkomen dat andere menu-opties dan 4 & 5 errors gooien omdat de blockchain None zou zijn (maar mogelijk netter om try except blocks te gebruiken in het menu?)
        self.wallet.create_keys()                               # Initiele keys genereren die worden opgeslagen in het Wallet object binnen dit Node object,                              
        self.blockchain = Blockchain(self.wallet.public_key)    # en vervolgens een blockchain object aanmaken die een id krijgt obv de gegenereerde public key


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
            print('4: Create wallet')
            print('5: Load wallet')
            print('6: Save keys')
            print('q: Quit')

            user_choice = self.get_user_choice()
            
            if user_choice == '1':
                tx_data = self.get_transaction_values()  
                recipient, amount = tx_data         # unpacken van de tuple 'tx_data' en diens values in de variabelen 'recipient' en 'amount' stoppen
                # Add the transaction to the open_transactions list
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)     # Mbv sign_transaction() een signature (string) gereturned krijgen voor de transaction
                # if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):      # kwarg 'amount' zodat het tweede argument niet voor de 'sender' parameter wordt gebruikt (die gebruikt dan de default 'owner' variabele)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount): 
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(f"Open transactions: {self.blockchain.open_transactions}")
            
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining failed. Got no wallet?')
            
            elif user_choice == '3':
                self.print_blockchain_elements()
            
            elif user_choice == '4':
                self.wallet.create_keys()                               # Nieuwe keys voor De bestaande keys (die bij initialisatie van de node zijn aangemaakt) overschrijven met nieuwe keys,
                self.blockchain = Blockchain(self.wallet.public_key)    # en vervolgens de blockchain aanmaken met een id die bestaat uit de public key die je zojuist o.a. hebt gegenereerd
                
            elif user_choice == '5':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)    # de ingeladen public_key gebruiken om een nieuwe blockchain object te instantieren (eigenijk net als bij menu-optie 4)
            
            elif user_choice == '6':
                self.wallet.save_keys()
            
            elif user_choice.upper() == 'Q':
                # break
                menu = False        # This will lead to the loop to exit because it's running condition becomes False
            
            else:
                print('Input was invalid, please pick a value from the list!')
            
            if not Verification.verify_chain(self.blockchain.chain):    # if verify_chain() returns False -> print a message
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break                           # Break out of the loop

            print(f"Balance of {self.wallet.public_key}: {self.blockchain.get_balance():.2f}")         # Pas als je de open transactions hebt gemined wordt de nieuwe balance van de node getoond. Note dat je de float limit tot maar 2 decimalen.

        # gets executed when the loop is done (doesn't work when you break out of the loop)
        else:
            print('User left')

        print('Done!')

# Wanneer je zelf een module/file runned dan wordt diens __name__ door Python als __main__ aangemerkt. 
# Als een module wordt geimporteerd is __name__ gelijk aan de naam van de module (in dit geval dus 'node')
# Het aanmaken van een Node object en daar vervolgens de listen_for_input() method op callen (zie hieronder), 
# mag dus alleen gebeuren wanneer de context of execution is dat je zelf direct de file aan het runnen bent.
# Handig als je bijvoorbeeld een module importeert, maar wilt voorkomen dat de code die daarin staat direct wordt uitgevoerd.
if __name__ == '__main__':      
    node = Node()
    node.listen_for_input()