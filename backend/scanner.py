from os import environ

from django import setup as django_setup

environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'backend.settings.{}'.format(
        environ.get('BACKEND_SETTINGS_MODE')
    ),
)
django_setup()


if __name__ == '__main__':
    from contracts.models import Contract
    from contracts.services.scanners.functions import start_scanners

    contract = Contract.get_contract_by_blockchain_id(
        blockchain_id=int(environ.get('BLOCKCHAIN_ID')),
    )

    start_scanners(
        scanners={
            contract.network.title: {
                'network': contract.network.title,
                'contract_address': contract.address,
                'start_block': int(environ.get('START_BLOCK')),
            },
        }
    )
