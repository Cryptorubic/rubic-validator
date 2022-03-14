from multiprocessing import Pool

from .base import Scanner, NearScanner
from .handlers import VALIDATOR_HANDLERS


def get_scanner(
    name: str,
    network_title: str,
    contract_address: str,
    start_block: int = None,
) -> Scanner:
    """
    Returns Scanner instance

    :param name: name of scanner for logging
    :param network_title: name of blockchain in DataBase
    :param contract_address: contract address which will be scanned
    :param start_block: block number from which start scanning
    """
    return Scanner(
        name=name,
        network=network_title,
        contract=contract_address,
        events=(
            'TransferTokensToOtherBlockchainUser',
            'TransferCryptoToOtherBlockchainUser',
        ),
        event_handlers=VALIDATOR_HANDLERS,
        start_block=start_block,
    )


def get_near_scanner(
    contract,
    graphql_link: str,
    graphql_query: str,
    start_timestamp,
) -> NearScanner:
    return NearScanner(
        graphql_link=graphql_link,
        graphql_query=graphql_query,
        start_timestamp=start_timestamp,
        network='near',
        contract=contract,
        event_name='TransferTokensToOtherBlockchainUser',
        event_handlers=VALIDATOR_HANDLERS,
    )


def start_scanners(scanners: dict):
    """
    Starts scanner instances in proccess pool.

    ---

    :scanners: dict
    {
        '<scanner_name aka network_title>': {
            'network': '<network_title>',
            'contract_address': 'contract_address',
            'start_block': int,
        },
        ...
    }
    """
    with Pool(processes=len(scanners)) as pool:
        for scanner, value in scanners.items():
            scanner_instance = get_scanner(
                name=f'{scanner}-scanner',
                network_title=value.get('network'),
                contract_address=value.get('contract_address'),
                start_block=value.get('start_block'),
            )

            pool.apply_async(scanner_instance.start())


def start_near_scanner(scanner: dict):
    """
    Starts NEAR scanner
    :param scanner: contains params for near scanner
    :type scanner: dict
    """

    get_near_scanner(
        contract=scanner.get('contract_address'),
        graphql_link=scanner.get('graphql_link'),
        graphql_query=scanner.get('graphql_query'),
        start_timestamp=scanner.get('start_timestamp'),
    ).scan()
