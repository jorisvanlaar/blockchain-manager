from flask import Flask, jsonify     # Flask importeren, zodat je een Flask applicatie kunt opzetten die dienstdoet als (web) server die kan luisteren naar inkomende HTTP requests van een client/webapp. jsonify zodat je data kunt converten naar JSON en terugsturen wanneer dat wordt gerequest
from flask_cors import CORS # CORS importeren zodat je de setup van de Flask app zodanig kan aanpassen dat je wel in de toekomst connecties van andere nodes met deze server kunt toestaan (dat mag standaard namelijk niet)
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)                       # Aanmaken van de Flask app/server en hangen aan de variabelen 'app'. Bij het aanmaken moet je als argument de naam van de app meegeven, in dit geval __name__ Dit vertelt Flask in welke context de node runnend. 
wallet = Wallet()                           # Direct bij het starten van de app een Wallet initialiseren, die per default nog geen keys heeft natuurlijk (zie constructor in de Wallet class)
blockchain = Blockchain(wallet.public_key)  # Initialiseren van de blockchain. Diens public_key zal in eerste instantie None zijn, maar dat maakt niet uit, want die heb ik toch niet nodig voor het returnen van de blockchain in het '/chain' endpoint
CORS(app)                                   # De Flask app/server wrappen in het CORS mechanisme, zodat de app nu ook potentieel connecties van andere clients/nodes accepteert


# De wallet is wel aangemaakt, maar diens keys zijn per default nog None, dat moet gefixed worden met deze function.
# Deze functie maakt keys aan, en slaat die op in een file op de server.
@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()        # Genereren van de keys voor de wallet
    if wallet.save_keys():      # En als het saven van de keys succesfull is (True wordt gereturned en de keys zijn opgeslagen in een 'wallet.txt' file),
        response = {            # Stuur dan als server deze respons terug, waarmee je de data terugstuurt van de keys.
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }
        global blockchain                           # Vertel de line hieronder dat de global 'blockchain' variabele moet worden gebruikt
        blockchain = Blockchain(wallet.public_key)  # Re-initialiseren van de blockchain, omdat die in eerste instantie None keys heeft, maar nu je de keys hebt gegenereerd wil je opnieuw de blockchain aanmaken met wel een public_key die content heeft.
        return jsonify(response), 201   # Convert de respons naar JSON data met een HTTP statuscode van 201 ('Created', The request has been fulfilled, resulting in the creation of a new resource.)
    else:                       # Maar maak deze respons aan als het saven van de keys mislukt.
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500   # Convert de respons naar JSON data met een HTTP statuscode van 500 ('Internal Server Error', oftewel een generic error message)
            


def load_keys():
    pass


# In Flask maak je endpoints aan mbv de "route" decorator die je toevoegt aan een function. Hiermee registreer je een nieuwe route binnen je Flask app.
# Deze decorator heeft 2 arguments nodig voor dit endpoint: 
# 1. De path (een url bestaat uit domain/path, oftewel: jorisvanlaar.nl/about.js bijv. jorisvanlaar.nl is de domain, about.js is de path)
# 2. Het type request
# Door alleen een '/' als path in te geven wordt dit endpoint bereikt (en dus get_ui() gecalled) als je navigeert naar localhost:5000/ in de browser. Eigenlijk is de path dus leeg.
# methods=['GET'] -> Alleen maar GET requests toestaan die naar dit endpoint kunnen worden verstuurd
# Op het moment dat de client een GET request verstuurd naar de path localhost:5000/ (oftewel 0.0.0.0:5000/) dan wordt de get_ui() functie gecalled die een response returned in de vorm van een string
# Als je dus node.py runned, zodat de server openstaat, en vervolgens naar de browser gaat en als adres 'localhost:5000/' ingeeft, zul je de string 'This works' zien.
@app.route('/', methods=['GET'])
def get_ui():
    return 'This works'


# Aanmaken POST request voor het minen van een block
@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block() # De block die wordt toegevoegd aan de blockchain, wordt gereturned door mine_block(). Dit block opslaan in de variabele 'block', maar dit block en diens transactions moet je converten naar dictionaries, omdat je die anders niet naar JSON data kunt converten, wat je nodig hebt voor het versturen van een response.

    if block != None:               # Als het gereturnde block niet None is, 
        dict_block = block.__dict__.copy()                                              # maak dan een kopie van de block en convert die naar een dictionary, 
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']] # en ook mbv een list comprehension alle transaction in het block converten naar dictionaries.
        
        response = {                                    # maak een response aan in de vorm van een dictionary, die o.a. bestaat uit het block dat is toegevoegd aan de blockchain
            'message': 'Block added successfully',
            'block': dict_block
        }
        return jsonify(response), 201                   # De response van de server op de request van de client/webapp als het minnen succeed, is dus een response-dictionary (geconvert naar JSON) met daarin het block dat is toegevoegd aan de blockchain, en een HTTP statuscode van 201 ('Created', The request has been fulfilled, resulting in the creation of a new resource.)
    else:                                               # Op het moment dat de mine_block() None returned en dus is gefailed (omdat bijv. de hosting_node/public_key van de blockchain None is),
        response = {                                    # maak dan een respons aan in de vorm van een dictionary, zodat je een wat complexere response kan terugsturen, die wat meer duidelijkheid over het failen bevat.
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key != None,     # dit is dus True als de blockchain een public_key heeft
        }
        return jsonify(response), 500                       # De response van de server op de request van de client/webapp als het minnen failed is dus een response-dictionary (geconvert naar JSON) en een HTTP statuscode van 500 ('Internal Server Error', oftewel een generic error message)


# Aanmaken van een route/endpoint die de huidige blockchain returned
# Omdat path '/chain' is, return je dus de current blockchain als je navigeert naar 'localhost:5000/chain' in de browser.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain = blockchain.chain
    # De chain is opgebouwd uit Blocks. Een object (in dit geval een Block) is nooit te converten naar json data,
    # daarom eerst het Block object converten naar een dictionary, want die is wel als json op te slaan.
    dict_chain = [block.__dict__.copy() for block in chain] # Mbv list comprehension door elk block van de chain gaan en die converten naar een dictionary, want die kun je wel met jsonify() converten naar JSON data.
                                                            # Is hierbij van belang dat je van elk block een copy maakt voordat je hem convert naar een dictionary, om ongewenste bijkomendheden te voorkomen wanneer je een block manipuleert. Die manipulatie doe je dan liever niet op het origineel.
    
    # block.__dict__ convert wel de blocks in de chain naar dictionaries, 
    # maar die convert niet OOK de transactions (oftewel een list aan Transactions) binnen dit object (de block) naar dictionaries.
    # Dus met een for-loop door elk reeds geconverte block van de chain gaan, en de transactions in elk block ook converten naar een dictionary.
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']] # mbv list comprehension de transactions in elk block converten naar dictionaries

    # return (dus eigenlijk de response van de server) in Flask vereist een tuple die bestaat uit:
    # 1. De data van de response (in dit geval dus de chain in de vorm van JSON data)
    # 2. De HTTP status code (in dit geval 200, wat staat voor 'OK' -> Standard response for successful HTTP requests)
    return jsonify(dict_chain), 200       # jsonify(chain) -> converten van de chain naar JSON-data, returnen van de 200 HTTP statuscode (OK)


if __name__ == '__main__':                  # Checken of de context is dat je node.py direct runned (en dus niet importeert)
    app.run(host='0.0.0.0', port=5000)      # run() -> Opstarten van de app/server, zodat ie gaat luisteren naar binnekomende HTTP requests
                                            # run() neemt twee argumenten: Het IP waarop we willen runnen (0.0.0.0 oftewel localhost/deze computer), 
                                            # en de PORT waarop we willen luisteren naar requests, in dit geval 5000 maar dat is een willekeurig duizendtal omdat die portnummers vaak ongebruikt zijn.



    


