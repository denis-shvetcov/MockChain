import copy
import hashlib
import os
import random
import string
import sys
import threading

import requests

from block import Block
from exceptions import *


class Node:
    chain = []
    nonce = 0
    nonce_mode = os.environ['nonce']
    running = True
    nodes = os.environ['nodes'].split(',')
    port = int(os.environ['port'])

    def checkCompatibility(self, block):
        if len(self.chain) > 0:
            if block.previous_hash != self.chain[-1].hash:
                raise HashNotMatch
            if block.index <= self.chain[-1].index:
                raise OldBlock
            if block.index > self.chain[-1].index + 1:
                raise LongestChain
        else:
            if block.index != 1:
                raise InvalidIndex

    def addBlockToChain(self, block):
        try:
            self.checkCompatibility(block)
            self.chain.append(block)
            return True
        except Exception as e:
            print(e)
            return False

    def sending(self, block):
        for node in self.nodes:
            try:
                requests.post("http://{}/receiver".format(node),
                              json={"index": block.index, "previous_hash": block.previous_hash, "data": block.data,
                                    "nonce": block.nonce, "hash": block.hash, "port": self.port})
            except Exception as e:
                print(e)

    def changeNonce(self):
        if self.nonce_mode == "inc":
            if self.nonce == sys.maxsize:
                self.nonce = - sys.maxsize
            else:
                self.nonce += 1
        elif self.nonce_mode == "dec":
            if self.nonce == - sys.maxsize:
                self.nonce = sys.maxsize
            else:
                self.nonce -= 1
        else:
            self.nonce = random.randint(-sys.maxsize, sys.maxsize)

    def generateBlocks(self):
        while self.running:
            if len(self.chain) != 0:
                previous_hash = self.chain[-1].hash
                index = self.chain[-1].index + 1
            else:
                previous_hash = ''
                index = 1
            data = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(256))
            while self.running:
                try:
                    b_hash = hashlib.sha256(
                        (str(index) + previous_hash + data + str(self.nonce)).encode('utf-8')).hexdigest()
                    block = Block(index, previous_hash, data, self.nonce, b_hash)
                    if self.addBlockToChain(block):
                        print("my block: {}".format(block))
                        sender = threading.Thread(target=self.sending, args=(block,))
                        sender.start()
                        break
                except InvalidHash:
                    self.changeNonce()

    def chainLoader(self, last_index, source):
        cursor_index = int(last_index)
        temp_chain = copy.deepcopy(self.chain)
        blocks_storage = []
        while cursor_index >= 1:
            try:
                result = requests.get("http://{}/get_block".format(source), params={'index': cursor_index})
                block_data = result.json()
                block = Block(block_data['index'], block_data['previous_hash'], block_data['data'], block_data['nonce'],
                              block_data['hash'])
                if block.index == len(self.chain) + 1:
                    added = self.addBlockToChain(block)
                    if added:
                        print("new block from {}: {}".format(source, block))
                        break
                    del self.chain[-1]
                blocks_storage.append(block)
                cursor_index -= 1
            except Exception as e:
                print(e)
                self.chain = temp_chain
                return False
        while len(blocks_storage) > 0:
            block = blocks_storage.pop()
            added = self.addBlockToChain(block)
            if not added:
                self.chain = temp_chain
                return False
            else:
                print("new block from {}: {}".format(source, block))
        return True
