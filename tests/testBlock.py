import hashlib
import random
import string
import unittest

from block import Block
from exceptions import InvalidHash


class BlockTests(unittest.TestCase):

    def testInvalidBlockCreating(self):
        self.assertRaises(InvalidHash, Block, 1, "aaa", "bbb", 1, "cccc")
        self.assertRaises(InvalidHash, Block, 1, "aaa", "bbb", 1, "cccc0000")
        previous_hash = ''
        index = 1
        data = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(256))
        nonce = 1
        b_hash = ""
        while not b_hash.endswith("00000"):
            b_hash = hashlib.sha256(
                (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
            if b_hash.endswith("00000"):
                Block(index, previous_hash, data, nonce, b_hash)
            else:
                self.assertRaises(InvalidHash, Block, index, previous_hash, data, nonce, b_hash)
                nonce += 1
