import hashlib

from exceptions import InvalidHash


class Block:
    def __init__(self, index, previous_hash, data, nonce, b_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.nonce = nonce
        self.hash = b_hash
        self.checkHash()

    def checkHash(self):
        if not (hashlib.sha256((str(self.index) + self.previous_hash + self.data + str(self.nonce)).encode(
                'utf-8')).hexdigest() == self.hash and self.hash.endswith("00000")):
            raise InvalidHash

    def __str__(self):
        return "index = {}\n prev_hash = {}\n hash = {}\n".format(self.index, self.previous_hash, self.hash)
