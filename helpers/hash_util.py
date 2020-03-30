import hashlib
import json

def hash_string_256(string):
    """ Creates a hash for a given string """
    return hashlib.sha256(string).hexdigest()


def hash_block(block):
    """ Hashes a block and returns this hash in the form of a string """     
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']] 
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())