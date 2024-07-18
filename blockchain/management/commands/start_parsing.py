import asyncio
from django.core.management.base import BaseCommand
from ...parser import parse_blockchain
from ...worker import address_worker


class Command(BaseCommand):
    help = 'Start the parser and worker'

    def handle(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())


async def run():
    parser_task = asyncio.create_task(parse_blockchain())
    worker_task = asyncio.create_task(address_worker())

    await parser_task
    await worker_task
