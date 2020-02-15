import hashlib
import json         # geimporteerd omdat je mbv json objecten kunt encoden als een string (wat je wilt voor het encoden van een block naar een string in de hash-function)


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()

def hash_block(block):
    """ Hashes a block and returns this hash in the form of a string (thats separated by -'s using list comprehension) """
    # return '-'.join([str(block[key]) for key in block])   # ipv een pseudo-hash in string-vorm, een echte hash gebruiken mbv hashlib
    # return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()      
    return hash_string_256(json.dumps(block, sort_keys=True).encode())  # ipv de syntax de line hierboven, kan het korter door gebruik te maken van een aparte, custom hash_string_256() function
    
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