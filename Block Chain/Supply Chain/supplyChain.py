import hashlib
import json
import time
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import os

# Generate/load RSA key pairs for users
def generate_keys(name):
    if os.path.exists(f"{name}_private.pem") and os.path.exists(f"{name}_public.pem"):
        with open(f"{name}_private.pem", "r") as f:
            private_key = RSA.import_key(f.read())
        with open(f"{name}_public.pem", "r") as f:
            public_key = RSA.import_key(f.read())
    else:
        key = RSA.generate(2048)
        private_key = key
        public_key = key.publickey()
        with open(f"{name}_private.pem", "wb") as f:
            f.write(private_key.export_key())
        with open(f"{name}_public.pem", "wb") as f:
            f.write(public_key.export_key())
    return private_key, public_key

# Utility to sign data
def sign_data(private_key, data):
    h = SHA256.new(data.encode())
    signature = pkcs1_15.new(private_key).sign(h)
    return signature.hex()

# Utility to verify signature
def verify_signature(public_key, data, signature_hex):
    h = SHA256.new(data.encode())
    signature = bytes.fromhex(signature_hex)
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

class Transaction:
    def __init__(self, product_id, sender, receiver, location, description, timestamp=None, signature=None):
        self.product_id = product_id
        self.sender = sender
        self.receiver = receiver
        self.location = location
        self.description = description
        self.timestamp = timestamp or time.time()
        self.signature = signature  # hex string

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "location": self.location,
            "description": self.description,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }

    def sign_transaction(self, private_key):
        tx_data = json.dumps({
            "product_id": self.product_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "location": self.location,
            "description": self.description,
            "timestamp": self.timestamp,
        }, sort_keys=True)
        self.signature = sign_data(private_key, tx_data)

    def verify_transaction(self, public_key):
        tx_data = json.dumps({
            "product_id": self.product_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "location": self.location,
            "description": self.description,
            "timestamp": self.timestamp,
        }, sort_keys=True)
        return verify_signature(public_key, tx_data, self.signature)


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = [tx.to_dict() for tx in transactions]
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_data.encode()).hexdigest()

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash[:10]}..., prev_hash={self.previous_hash[:10]}...)"

class SupplyChainBlockchain:
    def __init__(self, difficulty=4, max_transactions=3):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions = []
        self.max_transactions = max_transactions
        self.participants = {}  # name -> public key

    def create_genesis_block(self):
        return Block(0, [], time.time(), "0")

    def register_participant(self, name, public_key):
        self.participants[name] = public_key
        print(f"Participant '{name}' registered.")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        # Verify transaction signature
        sender_key = self.participants.get(transaction.sender)
        if sender_key is None:
            print(f"Sender {transaction.sender} not registered.")
            return False
        if not transaction.verify_transaction(sender_key):
            print(f"Invalid signature for transaction from {transaction.sender}.")
            return False
        self.pending_transactions.append(transaction)
        print(f"Transaction from {transaction.sender} added.")
        return True

    def mine_pending_transactions(self):
        if not self.pending_transactions:
            print("No transactions to mine.")
            return

        tx_to_mine = self.pending_transactions[:self.max_transactions]
        block = Block(
            index=len(self.chain),
            transactions=tx_to_mine,
            timestamp=time.time(),
            previous_hash=self.get_latest_block().hash
        )
        self.proof_of_work(block)
        self.chain.append(block)
        print(f"Block #{block.index} mined with {len(tx_to_mine)} transactions.")

        self.pending_transactions = self.pending_transactions[self.max_transactions:]

    def proof_of_work(self, block):
        print("Mining block...")
        while block.hash[:self.difficulty] != "0" * self.difficulty:
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Block mined: {block.hash}")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            # Validate hash
            if current.hash != current.calculate_hash():
                print(f"Hash mismatch at block {current.index}!")
                return False
            # Validate previous hash linkage
            if current.previous_hash != prev.hash:
                print(f"Previous hash mismatch at block {current.index}!")
                return False
            # Validate transaction signatures
            for tx_dict in current.transactions:
                sender = tx_dict["sender"]
                signature = tx_dict["signature"]
                if sender not in self.participants:
                    print(f"Unknown sender {sender} in block {current.index}")
                    return False
                pub_key = self.participants[sender]
                tx_obj = Transaction(**tx_dict)
                if not tx_obj.verify_transaction(pub_key):
                    print(f"Invalid transaction signature in block {current.index}")
                    return False
        return True

    def print_chain(self):
        for block in self.chain:
            print(json.dumps({
                "index": block.index,
                "hash": block.hash,
                "prev_hash": block.previous_hash,
                "timestamp": datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "transactions": block.transactions
            }, indent=4))


# === Usage Example ===

# Generate keys for participants (Farmer, Distributor, Retailer)
farmer_priv, farmer_pub = generate_keys("FarmerJoe")
distributor_priv, distributor_pub = generate_keys("DistributorMike")
retailer_priv, retailer_pub = generate_keys("RetailerLisa")

blockchain = SupplyChainBlockchain()

# Register participants with their public keys
blockchain.register_participant("FarmerJoe", farmer_pub)
blockchain.register_participant("DistributorMike", distributor_pub)
blockchain.register_participant("RetailerLisa", retailer_pub)

# Farmer creates and signs a transaction
tx1 = Transaction(
    product_id="PRD001",
    sender="FarmerJoe",
    receiver="DistributorMike",
    location="Farmville",
    description="Harvested 100kg apples"
)
tx1.sign_transaction(farmer_priv)
blockchain.add_transaction(tx1)

# Distributor creates and signs a transaction
tx2 = Transaction(
    product_id="PRD001",
    sender="DistributorMike",
    receiver="RetailerLisa",
    location="Central Warehouse",
    description="Shipped 100kg apples"
)
tx2.sign_transaction(distributor_priv)
blockchain.add_transaction(tx2)

# Mine the block containing above transactions
blockchain.mine_pending_transactions()

# Retailer sells to customer (no signature needed as "Customer" is outside network)
tx3 = Transaction(
    product_id="PRD001",
    sender="RetailerLisa",
    receiver="Customer",
    location="Downtown Store",
    description="Sold 10kg apples"
)
tx3.sign_transaction(retailer_priv)
blockchain.add_transaction(tx3)

blockchain.mine_pending_transactions()

# Print blockchain and verify
blockchain.print_chain()
print("Blockchain valid?", blockchain.is_chain_valid())
