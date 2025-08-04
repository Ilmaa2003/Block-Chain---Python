import hashlib
import time

class Block:
    def __init__(self, index, timestamp, student_name, subject, marks, result, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.student_name = student_name
        self.subject = subject
        self.marks = marks
        self.result = result
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.index}{self.timestamp}{self.student_name}{self.subject}{self.marks}{self.result}{self.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

    def __str__(self):
        return (
            f"Index: {self.index}\n"
            f"Time: {self.timestamp}\n"
            f"Student: {self.student_name}\n"
            f"Subject: {self.subject}\n"
            f"Marks: {self.marks}\n"
            f"Result: {self.result}\n"
            f"Hash: {self.hash}\n"
            f"Previous Hash: {self.previous_hash}\n"
            + "-"*50
        )

class StudentBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.time(), "None", "None", 0, "None", "0")

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, student_name, subject, marks, pass_mark=50):
        result = "Pass" if marks >= pass_mark else "Fail"
        last_block = self.get_last_block()
        new_block = Block(len(self.chain), time.time(), student_name, subject, marks, result, last_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != prev.hash:
                return False
        return True

    def print_chain(self):
        for block in self.chain:
            print(block)

# Example usage
blockchain = StudentBlockchain()

# Adding some student exam results
blockchain.add_block("Alice", "Math", 76)
blockchain.add_block("Bob", "Science", 42)
blockchain.add_block("Charlie", "English", 58)

# Print the blockchain
blockchain.print_chain()

# Check chain validity
print("Blockchain valid?", blockchain.is_chain_valid())
