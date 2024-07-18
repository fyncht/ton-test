import asyncio
import time
from ton import TonlibClient
from .models import Address
from asgiref.sync import sync_to_async


async def address_worker():
    TonlibClient.enable_unaudited_binaries()  # Включаем использование неаудированных бинарных файлов
    ton_client = TonlibClient()
    await ton_client.init_tonlib()

    while True:
        addresses = await sync_to_async(list)(Address.objects.filter(status=0))
        for address in addresses:
            try:
                await process_address(ton_client, address)
            except Exception as e:
                print(f"Error processing address {address}: {e}")
        await asyncio.sleep(10)


async def process_address(ton_client, address):
    try:
        contract = await ton_client.raw_get_account_state(address=address.address)
        address.code = contract['code']
        address.data = contract['data']
        address.status = 1
        address.status_updated_at = int(time.time())
        await sync_to_async(address.save)()
    except Exception as e:
        print(f"Error processing address {address}: {e}")
