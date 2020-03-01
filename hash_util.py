import hashlib
import json         # geimporteerd omdat je mbv json, objecten kunt encoden als een string (wat je wilt voor het encoden van een block naar een string in de hash-function)


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()   # hexdigest() om van de hash die sha256() creeert een leesbare string te maken anders kan je erg geen checks op uitvoeren (zoals bijv. het voldoen aan de PoW criteria van twee nullen)

def hash_block(block):
    """ Hashes a block and returns this hash in the form of a string """    
    
    # Een object (in dit geval een Block) is nooit te converten naar json data (string in dit geval),
    # daarom eerst het Block object converten naar een dictionary, want die is wel als json op te slaan
    # Het is belangrijk hierbij om een kopie te maken van het block dat je wilt gaan hashen, omdat je het block wilt wijzigen voordat je hem hashed, en je wil het originele block ongewijzigd wilt laten.
    # __dict__ convert namelijk wel de block naar een dictionary, maar die convert niet OOK een list aan objecten (de transactions, oftewel een list aan Transactions) binnen dit object (de block) naar dictionaries. 
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']] # mbv een list comprehension door de transactions van het ingegeven block gaan en elke transaction converten naar een OrderedDict, zodat je de order van de transactions kunt waarborgen en je die wel kunt dumpen naar json data (wat met een list aan Transaction objecten niet kon)
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())  # gebruikmaken van de hash_string_256() method om een hash van het block te returnen
    

    # de json.dumps(hashable_block).encode() encode een hashable_block naar een string
    # de hashlib.sha256() method is een algoritme die een 64-character hash creeert obv een string, en zorgt ervoor dat dezelfde input altijd tot dezelfde hash leidt (wat nodig is om de hash van het vorige block te kunnen validaten)
    # de hexdigest() method convert de 'bytehash' die wordt gegenereerd door sha256() naar een gewone string

    # Zowel een block als een transaction zijn dictionaries. Het probleem van dictionaries is dat ze unordered zijn. 
    # Dit kan betekenen dat de volgorde van de key-value pairs van een block of transaction kan veranderen, 
    # Wat weer kan betekenen dat het hashen van een block verschillende hashes voor dezelfde block kan opleveren, omdat de order van een block en/of transaction kan zijn veranderd.
    # Het gevolg hiervan is dat een correct block bij het checken van de hash alsnog als invalid kan worden gezien.
    # Dit is te fixen met het named argument 'sort_keys' voor de json.dumps() method. Dit zorgt ervoor dat de keys van de dictionary gesorteerd worden voordat deze gedumpt wordt naar een string.
    # Wat betekent dat dezelfde dictionary altijd tot dezelfde string/hash leidt, ook al wijzigt de volgorde van de dictionary.
    # Het vastzetten van de order voor de transaction-dictionaries die je gebruikt in valid_proof() doe je door een OrderedDict te gebruiken ipv een standaard dictionary in add_transaction() en mine_block()
    # OrderedDict waarborgt dat de keys van de transactions altijd dezelfde order hebben