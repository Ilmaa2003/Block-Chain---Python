# 📦 Supply Chain Blockchain with Digital Signatures

This project is a Python-based blockchain implementation designed for tracking supply chain transactions using cryptographic security. It demonstrates how producers, distributors, and retailers can interact transparently using digitally signed transactions on a secure blockchain.

---

## 🚀 Features

- ✅ Custom block structure with SHA-256 hashing
- 🔐 Digital signature verification using RSA keys
- 🏗 Proof-of-Work (PoW) for block mining
- 📜 Transaction integrity and participant authentication
- 📦 Simulated product flow (Farm → Distributor → Retailer → Customer)
- 📂 Persistent RSA key generation and reuse

---

## 🧑‍🌾 Example Use Case

- **FarmerJoe** harvests apples and sends them to **DistributorMike**
- **DistributorMike** ships the apples to **RetailerLisa**
- **RetailerLisa** sells them to a **Customer**
- Each transaction is signed and verified before being mined into the blockchain

---

## 🔧 Requirements

- Python 3.7+
- `pycryptodome` library for RSA & digital signatures

Install dependencies:

```bash
pip install pycryptodome

## 📚 How it Works Internally

Each transaction includes:
- Sender
- Receiver
- Message
- Signature

🔁 Transactions are stored in a queue until mined.

⛏️ When mining, a valid hash is found (starts with `"0000"`).

🧱 Mined blocks are added to the chain with:
- Timestamps
- Previous block hash

---

## 🔍 Verification Logic

Each block:
- Stores the previous block hash
- Verifies digital signatures of all transactions
- Has a valid hash based on the contents and nonce

⚠️ If any data changes → hash changes → chain breaks

---

## 🚀 Future Enhancements

- 🌐 Web dashboard (Flask + React)
- 📱 QR-code tracking for products
- 🛡️ AES encryption for private data
- 🧪 Unit testing and error handling

---

## 🎓 Learning Goals

- ✅ Understand how blockchain applies to real-world use cases  
- ✅ Implement RSA digital signatures in Python  
- ✅ Build a mini PoW blockchain from scratch  
- ✅ Simulate authenticated supply chain transactions

---

## 📃 License

This project is licensed under the **MIT License**.

