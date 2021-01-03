import os
import time
import json
import random
import urllib3

REWIND_AFTER = 30
CHECK_INTERVAL = 5
RANDOM_WAITING_TIME = 10
RPC_URL = "http://127.0.0.1:8505/"


def main():
    print('Start watching IDChain...')
    last_seen_block = 0
    test_file = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'reset.it')

    while True:
        time.sleep(CHECK_INTERVAL)

        # rewind if there is ./reset.it file
        if os.path.exists(test_file):
            block_number = execute("eth_blockNumber", [])
            print(f'test rewind...\ncurent block: {int(block_number, 16)}')
            rewind(int(block_number, 16))
            os.remove(test_file)

        block_number = execute("eth_blockNumber", [])
        block = execute("eth_getBlockByNumber", [block_number, True])
        last_seen_block = max(int(block['number'], 16), last_seen_block)

        # if blocks are getting mined actively
        if time.time() - int(block['timestamp'], 16) < REWIND_AFTER:
            continue

        print(f"\n{time.strftime('%X %x')} locked at {last_seen_block}")
        # wait random time to allow generally only one node rewind
        random_wait = random.randint(0, RANDOM_WAITING_TIME)
        print(f'waiting for {random_wait} seconds before rewind')
        time.sleep(random_wait)
        # check if deadlock resolved by rewinding other nodes
        block_number = execute("eth_blockNumber", [])
        block = execute("eth_getBlockByNumber", [block_number, True])
        if time.time() - int(block['timestamp'], 16) < REWIND_AFTER:
            print('deadlock seems to be resolved by others')
            continue
        rewind(last_seen_block)


def rewind(last_seen_block):
    # set rewind target based on number of signers
    signers = execute("clique_getSigners", [])
    target = last_seen_block - (len(signers) // 2 + 1)
    execute("miner_stop", [])
    execute("debug_setHead", [hex(target)])
    execute("miner_start", [])
    print(f'rewinding to {target}!\n')
    time.sleep(CHECK_INTERVAL * 2)


def execute(cmd, params):
    payload = json.dumps(
        {"jsonrpc": "2.0", "method": cmd, "params": params, "id": 1})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    http = urllib3.PoolManager()
    try:
        resp = http.request("POST", RPC_URL, body=payload, headers=headers)
    except Exception as e:
        # if node is not started after restart yet
        time.sleep(CHECK_INTERVAL * 2)
        print(f'Error: {e}')
        return execute(cmd, params)
    return json.loads(resp.data)['result']


if __name__ == '__main__':
    main()
