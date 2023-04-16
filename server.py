import os
import threading

from block import Block
from node import Node
from flask import Flask, request, jsonify

app = Flask(__name__)
node = Node()

thread_gen = threading.Thread(target=node.generateBlocks)


@app.route('/receiver', methods=['POST'])
def receiver():
    global thread_gen
    block_data = request.json
    if block_data['index'] > len(node.chain):
        if thread_gen.is_alive():
            node.running = False
            thread_gen.join()
        try:
            block = Block(block_data['index'], block_data['previous_hash'], block_data['data'], block_data['nonce'],
                          block_data['hash'])
            if node.addBlockToChain(block):
                print("new block from network: {}".format(block))
            else:
                node.chainLoader(block_data['index'], request.environ['REMOTE_ADDR'] + ":" + str(block_data['port']))
        except Exception as e:
            print(e)
        thread_gen = threading.Thread(target=node.generateBlocks)
        node.running = True
        thread_gen.start()
    return '', 204


@app.route('/get_block')
def get_block():
    block_index = int(request.args['index'])
    if block_index > len(node.chain) or block_index < 1:
        print(block_index > len(node.chain))
        print(block_index < 1)
        print("error")
        return "error"
    block = node.chain[block_index - 1]
    return jsonify(
        index=block.index,
        previous_hash=block.previous_hash,
        data=block.data,
        nonce=block.nonce,
        hash=block.hash
    )


if __name__ == "__main__":
    if 'genesis' in os.environ:
        if os.environ['genesis'].lower() == "true":
            thread_gen.start()
    app.run(host="0.0.0.0", port=node.port)
