from Crypto.PublicKey import RSA    # de pycryptodom package importeren (die gek genoeg Crypto heet bij het importeren), en daarvan specifiek het RSA algoritme importeren voor het genereren van public/private keys 
import Crypto.Random                # Random van de pycrypto/Crypto package importeren, zodat je een random nummer kunt genereren
import binascii                     # impporteren zodat je de public/private keys kunt converten van binary data  naar ascii data (string in dit geval)

class Wallet:
    def __init__(self):
        self.private_key = None     # None, want je wilt niet bij het aanmaken van een Wallet object aannemen dat een user per definitie keys wilt creeeren, mogelijk wil hij bestaande keys inladen. 
        self.public_key = None
    

    def create_keys(self):
        """ Creates a private and public key """
        private_key, public_key = self.generate_keys()  # de tuple die gereturned wordt door generate_keys() unpacken naar de variabelen 'private_key' en 'public_key'
        self.private_key = private_key
        self.public_key = public_key 
        
    
    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet.txt', 'w') as file:
                    file.write(self.public_key)
                    file.write('\n')
                    file.write(self.private_key)
            except(IOError, IndexError):
                print('Saving wallet failed')
        

    def load_keys(self):
        try:
            with open('wallet.txt', 'r') as file:
                keys = file.readlines()             # readlines() returned een list aan strings
                public_key = keys[0][:-1]           # slicing om het laatste karakter van de eerste line in de file te excluded, want dat is de '\n'
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
        except(IOError, IndexError):
            print('Loading wallet failed')

    
    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)  # 1024 staat voor het aantal bits van de keys, hoe hoger des te veiliger
                                                                    # Crypto.Random.new() geeft een random nummer, .read erachter zodat het random nummer ingelezen kan worden door de generate_keys() method 
        public_key = private_key.publickey()                        # de publickey() method return de publick key die hoort bij de ingegeven private key, dit duo aan keys werkt dus alleen maar samen                       
                                                        
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))  
        # returnen van een tuple met daarin een string-versie van de private & public key. 
        # private_key.exportKey(format='DER') -> de key encoden in een binary format,
        # binascii.hexlify(private_key) -> de binary encoded key converten naar een hexadecimal representatie hiervan   
        # .decode('ascii') -> en vervolgens die hexadecimal representatie van de key converten naar ascii karakters (oftewel een string)