import os
import django
import asyncio
import logging
from asgiref.sync import sync_to_async
from pytoniq import LiteClient
import socket
import struct

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ton_parser.ton_parser.settings')
django.setup()

from .models import Address

logging.basicConfig(level=logging.INFO)

@sync_to_async
def save_address_to_db(address, raw_data):
    try:
        Address.objects.create(
            address=address,
            raw_data=raw_data,
            status=0
        )
        logging.info(f"Address saved: {address}")
    except Exception as e:
        logging.error(f"Error saving address to DB: {e}")

def tlobject_to_dict(tlobject):
    if isinstance(tlobject, dict):
        return {key: tlobject_to_dict(value) for key, value in tlobject.items()}
    elif isinstance(tlobject, list):
        return [tlobject_to_dict(element) for element in list(tlobject)]
    elif hasattr(tlobject, '__dict__'):
        return tlobject_to_dict(vars(tlobject))
    else:
        return tlobject

def int_to_ip(ip_int):
    return socket.inet_ntoa(struct.pack('!I', ip_int))

async def parse_blockchain():
    logging.info("Starting blockchain parsing...")

    ip_int = 84478511  # Пример значения, замените на реальное
    host = int_to_ip(ip_int)
    port = 19949
    server_pub_key = 'n4VDnSCUuSpjnCyUk9e3QOOd6o0ItSWYbTnW3Wnn8wk='

    lite_client = LiteClient(host, port, server_pub_key)
    if lite_client is None:
        logging.error("Failed to initialize LiteClient")
        return

    await lite_client.connect()  # явная инициализация клиента

    try:
        logging.info("Sending get_masterchain_info request...")
        response = await lite_client.get_masterchain_info()
        if response is None:
            logging.error("Received None response from get_masterchain_info")
            return

        response_dict = tlobject_to_dict(response)
        logging.info(f"Masterchain Info Response: {response_dict}")

        if isinstance(response_dict, dict):
            if 'last' in response_dict and 'state_root_hash' in response_dict and 'init' in response_dict:
                latest_block = response_dict['last']
                logging.info(f"Latest block details: {latest_block}")

                if isinstance(latest_block, dict) and 'seqno' in latest_block:
                    await process_block(latest_block, lite_client)
                else:
                    logging.error(f"Invalid 'last' block structure: {latest_block}")
            else:
                logging.error(f"Response missing required keys: {response_dict}")
        else:
            logging.error(f"Invalid response type: {type(response_dict)}, content: {response_dict}")
    except Exception as e:
        logging.error(f"Error in parse_blockchain: {e}")


async def process_block(block, lite_client, retries=10):
    for attempt in range(retries):
        try:
            logging.info(f"Processing block: {block}")

            workchain = block.get('workchain')
            shard = block.get('shard')
            seqno = block.get('seqno')
            root_hash = block.get('root_hash')
            file_hash = block.get('file_hash')

            logging.debug(
                f"Block details: workchain={workchain}, shard={shard}, seqno={seqno}, root_hash={root_hash}, file_hash={file_hash}")

            if None in (workchain, shard, seqno, root_hash, file_hash):
                logging.error(f"Block has missing values: {block}")
                return

            logging.info(
                f"Calling get_block with workchain: {workchain}, shard: {shard}, seqno: {seqno}, root_hash: {root_hash}, file_hash: {file_hash}")
            block_details = await lite_client.get_block(workchain, shard, seqno, root_hash, file_hash)

            if block_details is None:
                logging.error(f"Received None response from get_block for block: {block}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue

            logging.info(f"Received block details: {block_details}")

            block_details_dict = tlobject_to_dict(block_details)
            logging.info(f"Block Details Response: {block_details_dict}")

            if "transactions" in block_details_dict:
                logging.info(f"Found {len(block_details_dict['transactions'])} transactions in block")
                for transaction in block_details_dict["transactions"]:
                    await process_transaction(transaction, lite_client)
            else:
                logging.info("No transactions found in block")
            break  # Exit loop if successful
        except Exception as e:
            logging.error(f"Error in process_block on attempt {attempt + 1}: {e}")
            if attempt + 1 == retries:
                logging.error(f"Failed to process block after {retries} attempts")
            else:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff


async def process_transaction(transaction, lite_client):
    try:
        logging.info(f"Processing transaction: {transaction}")
        if "in_msg" in transaction:
            in_msg = transaction["in_msg"]
            if "source" in in_msg:
                address = in_msg["source"]["account_address"]
                logging.info(f"Found source address: {address}")
                await save_address_to_db(address, in_msg)
            else:
                logging.info("No source address found in transaction")
        else:
            logging.info("No incoming message found in transaction")

        if "out_msgs" in transaction:
            for out_msg in transaction["out_msgs"]:
                if "destination" in out_msg:
                    address = out_msg["destination"]["account_address"]
                    logging.info(f"Found destination address: {address}")
                    await save_address_to_db(address, out_msg)
                else:
                    logging.info("No destination address found in outgoing message")
    except Exception as e:
        logging.error(f"Error in process_transaction: {e}")

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(parse_blockchain())
