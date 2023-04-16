import hashlib
import os
import random
import string
import sys
import threading
import time
import unittest

from block import Block
from exceptions import InvalidHash, InvalidIndex, HashNotMatch, OldBlock, LongestChain

os.environ['nonce'] = 'inc'
os.environ['nodes'] = 'test1,test2'
os.environ['port'] = '8080'

from node import Node


class NodeTests(unittest.TestCase):

    def testNonce(self):
        node = Node()
        old_nonce = node.nonce
        node.changeNonce()
        self.assertEqual(old_nonce, node.nonce - 1)
        node.nonce_mode = "dec"
        old_nonce = node.nonce
        node.changeNonce()
        self.assertEqual(old_nonce, node.nonce + 1)
        node.nonce = - sys.maxsize
        node.changeNonce()
        self.assertEqual(sys.maxsize, node.nonce)
        node.nonce_mode = "inc"
        node.changeNonce()
        self.assertEqual(- sys.maxsize, node.nonce)

    def testCheckComp(self):
        node = Node()
        previous_hash = ''
        data = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(256))
        nonce = 1
        index = 2
        while True:
            try:
                b_hash = hashlib.sha256(
                    (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
                block2 = Block(index, previous_hash, data, nonce, b_hash)
                self.assertRaises(InvalidIndex, node.checkCompatibility, block2)
                break
            except InvalidHash:
                nonce += 1
        index = 1
        while True:
            try:
                b_hash = hashlib.sha256(
                    (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
                block1 = Block(index, previous_hash, data, nonce, b_hash)
                node.checkCompatibility(block1)
                node.addBlockToChain(block1)
                break
            except InvalidHash:
                nonce += 1
        index = 3
        while True:
            try:
                b_hash = hashlib.sha256(
                    (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
                block3 = Block(index, previous_hash, data, nonce, b_hash)
                self.assertRaises(LongestChain, node.checkCompatibility, block3)
                break
            except InvalidHash:
                nonce += 1
        self.assertRaises(HashNotMatch, node.checkCompatibility, block2)
        self.assertRaises(OldBlock, node.checkCompatibility, block1)

    def testAddBlock(self):
        node = Node()
        previous_hash = ''
        data = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(256))
        nonce = 1
        index = 2
        while True:
            try:
                b_hash = hashlib.sha256(
                    (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
                block2 = Block(index, previous_hash, data, nonce, b_hash)
                self.assertFalse(node.addBlockToChain(block2))
                break
            except InvalidHash:
                nonce += 1
        index = 1
        while True:
            try:
                b_hash = hashlib.sha256(
                    (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
                block1 = Block(index, previous_hash, data, nonce, b_hash)
                self.assertTrue(node.addBlockToChain(block1))
                break
            except InvalidHash:
                nonce += 1
        index = 3
        while True:
            try:
                b_hash = hashlib.sha256(
                    (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
                block3 = Block(index, previous_hash, data, nonce, b_hash)
                self.assertFalse(node.addBlockToChain(block3))
                break
            except InvalidHash:
                nonce += 1
        self.assertFalse(node.addBlockToChain(block2))
        self.assertFalse(node.addBlockToChain(block1))
        for i in range(2, 5):
            index = i
            previous_hash = node.chain[-1].hash
            nonce = 0
            while True:
                try:
                    b_hash = hashlib.sha256(
                        (str(index) + previous_hash + data + str(nonce)).encode('utf-8')).hexdigest()
                    block = Block(index, previous_hash, data, nonce, b_hash)
                    self.assertTrue(node.addBlockToChain(block))
                    break
                except InvalidHash:
                    nonce += 1

    def testGenerator(self):
        node = Node()
        gen_thread = threading.Thread(target=node.generateBlocks)
        gen_thread.start()
        time.sleep(30)
        node.running = False
        gen_thread.join()
        self.assertFalse(gen_thread.is_alive())
        self.assertFalse(len(node.chain) == 0)
