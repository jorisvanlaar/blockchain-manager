from flask import Flask, jsonify, request, send_from_directory 
from wallet import Wallet
from blockchain import Blockchain
from helpers.verification import Verification

app = Flask(__name__)                       
wallet = Wallet()                           
blockchain = Blockchain(wallet.public_key)  


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/img/joris_coin.png', methods=['GET'])
def get_logo():
    return send_from_directory('img', 'joris_coin.png')


@app.route('/img/favicon.ico', methods=['GET'])
def get_favicon():
    return send_from_directory('img', 'favicon.ico')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()        
    if wallet.save_keys():      
        global blockchain                           
        blockchain = Blockchain(wallet.public_key)  
        response = {            
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201   
    else:                       
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500   
            

@app.route('/wallet', methods=['GET']) 
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance                                
        }
        return jsonify(response), 200                        
    else:
        response = {
            'message': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key != None      
        }
        return jsonify(response), 500                       


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:               
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400   
    
    tx_data = request.get_json()                                       
    if not tx_data:                   
        response = {
            'message': 'No data found.' 
        }
        return jsonify(response), 400   
    
    required_data = ['recipient', 'amount']   
    if not all(data in tx_data for data in required_data): 
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    
    recipient = tx_data['recipient']
    amount = tx_data['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)   

    success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount) 
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {                                
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block() 
    if block != None:               
        dict_block = block.__dict__.copy()                                              
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']] 
        
        response = {                                    
            'message': 'Block added successfully',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201                   
    else:                                               
        response = {                                    
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key != None,     
        }
        return jsonify(response), 500                       


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    open_transactions = blockchain.open_transactions                    
    dict_open_transactions = [tx.__dict__ for tx in open_transactions]
    return jsonify(dict_open_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain = blockchain.chain
    if not Verification.verify_chain(chain):    
        response = {
            'message': 'invalid'
        }
        return jsonify(response), 500
    else:
        dict_chain = [block.__dict__.copy() for block in chain] 
        for dict_block in dict_chain:
            dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']] 

        return jsonify(dict_chain), 200       


if __name__ == '__main__':                  
    app.run(host='0.0.0.0', port=5000)



    


