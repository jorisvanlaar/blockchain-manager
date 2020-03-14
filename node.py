from flask import Flask     # Flask importeren, zodat je een Flask applicatie kunt opzetten die dienstdoet als (web) server die kan luisteren naar inkomende HTTP requests van een client/webapp
from flask_cors import CORS # CORS importeren zodat je de setup van de Flask app zodanig kan aanpassen dat je wel in de toekomst connecties van andere nodes met deze server toestaat (dat mag standaard namelijk niet)
from wallet import Wallet

app = Flask(__name__)   # Aanmaken van de Flask app/server en hangen aan de variabelen 'app'. Bij het aanmaken moet je als argument de naam van de app meegeven, in dit geval __name__ Dit vertelt Flask in welke context het node runnend. 
wallet = Wallet()       # Direct bij het starten van de app een Wallet initialiseren, die per default nog geen keys heeft natuurlijk (zie constructor in de Wallet class)
CORS(app)               # De Flask app/server wrappen in het CORS mechanisme, zodat de app nu ook potentieel connecties van andere clients/nodes accepteert


# In Flask maak je endpoints aan mbv de "route" decorator die je toevoegt aan een function. Hiermee registreer je een nieuwe route binnen je Flask app.
# Deze decorator heeft 2 arguments nodig voor dit endpoint: de path (een url bestaat uit domain/path, oftewel: jorisvanlaar.nl/about.js bijv. jorisvanlaar.nl is de domain, about.js is de path), 
# en het type request.
# Door alleen een '/' als path in te geven wordt dit endpoint bereikt (en dus get_ui() gecalled) als je navigeert naar localhost:5000 in de browser. Eigenlijk is de path dus leeg.
# Alleen maar GET requests toestaan die naar dit endpoint kunnen worden verstuurd
# Op het moment dat de client een GET request verstuurd naar de path localhost:5000/ (oftewel 0.0.0.0:5000/) dan wordt de get_ui() functie gecalled die een response returned in de vorm van een string
# Als je dus node.py runned, zodat de server openstaat, en vervolgens naar de browser gaat en als adres 'localhost:5000/' ingeeft, zul je de string 'This works' zien.
@app.route('/', methods=['GET'])
def get_ui():
    return 'This works'



if __name__ == '__main__':      # Checken of de context is dat je node.py direct runned (en dus niet importeert)
    app.run(host='0.0.0.0', port=5000)     # Opstarten van de app/server, zodat ie gaat luisteren naar binnekomende HTTP requests
                                # run() neemt twee argumenten: Het IP waarop we willen runnen (0.0.0.0 oftewel localhost/deze computer), 
                                # en de PORT waarop we willen luisteren naar requests, in dit geval 5000 maar dat is een willekeurig duizendtal omdat die portnummers vaak ongebruikt zijn.



    


