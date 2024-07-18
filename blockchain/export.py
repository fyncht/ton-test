import json
from ton_parser.blockchain.models import Address


def export_addresses_to_json(file_path: str):
    addresses = Address.objects.all()
    address_list = [address_to_dict(addr) for addr in addresses]

    with open(file_path, 'w') as json_file:
        json.dump(address_list, json_file, indent=4)


def address_to_dict(address):
    return {
        "address": address.address,
        "raw_data": address.raw_data.hex(),
        "status": address.status,
        "code": address.code.hex() if address.code else None,
        "data": address.data.hex() if address.data else None,
        "status_updated_at": address.status_updated_at
    }


if __name__ == "__main__":
    export_addresses_to_json("addresses.json")
