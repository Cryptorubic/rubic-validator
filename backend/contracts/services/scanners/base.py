from logging import info
from multiprocessing import Process
from time import sleep
from typing import Union

from django.conf import settings
from web3.datastructures import AttributeDict

from base.support_functions.decorators import auto_restart
from base.support_functions.requests import send_post_request
from backend.consts import SCANNER_INFO
from networks.models import CustomRpcProvider, NearRpcProvider
from ...models import Contract


BLOCK_RANGE = settings.BLOCK_RANGE
MIN_CONFIRMATION_BLOCK_COUNT = settings.MIN_CONFIRMATION_BLOCK_COUNT
DEFAULT_SCANNER_TIMEOUT = settings.DEFAULT_SCANNER_TIMEOUT
DEFAULT_SCANNER_TIMEOUT_FAST = settings.DEFAULT_SCANNER_TIMEOUT_FAST


class Scanner(Process):
    """
    Scanner of EVM blockchains. After fetching transaction from logs execute
    Handler function.

    :param network: name of blockchain in DataBase
    :param contract: contract address which will be scanned
    :param events: list of events which need to check
    :param event_handlers: method for every type of event
    :param start_block: block number from which start scanning
    """

    def __init__(
        self,
        name: str,
        network: str,
        contract: str,
        events: Union[list, tuple],
        event_handlers: dict,
        start_block: int = None,
    ):
        super().__init__(name=name,)
        self._network = network
        self._contract = contract
        self._events = events
        self._event_handlers = event_handlers
        self._start_block = start_block

    @auto_restart
    def scan(self):
        info(f'Contract address: \"{self._contract}\".')
        info(f'Network title: \"{self._network}\".')

        contract = Contract.objects.get(
            address__iexact=self._contract,
            network__title__iexact=self._network
        )

        custom_rpc_provider = CustomRpcProvider(contract.network)

        # PS: Если у контракта нет связанных с ним транзакций, то начальный
        # номер блока будет равняться номеру блока создания контракта.
        last_proccessed_block = self._start_block \
            or contract.last_proccessed_block \
            or contract.block_number_of_creation

        from_block = last_proccessed_block + 1

        info(
            SCANNER_INFO.format(
                f'Proccess name: "{self.name}".'
                f' Start scanning the \"{contract.address}\" contract address'
                # f' in the \"{contract.network.rpc_url}\"...'
            )
        )

        while 1:
            custom_rpc_provider.url_number = 0

            current_block_number = custom_rpc_provider.get_current_block_number()

            if last_proccessed_block < current_block_number:
                from_block = last_proccessed_block + 1

            last_block = current_block_number - MIN_CONFIRMATION_BLOCK_COUNT

            # FOR DEBUG AND ALPHA- OR BETA-TESTS
            # from_block = 18_168_480
            # to_block = 18_169_400

            if last_block - from_block > BLOCK_RANGE:
                to_block = from_block + BLOCK_RANGE
                timeout = DEFAULT_SCANNER_TIMEOUT_FAST
            elif last_block - from_block <= 0:
                timeout = DEFAULT_SCANNER_TIMEOUT

                info(
                    SCANNER_INFO.format(
                        f'\nSCANNER: \"{self.name.upper()}\".\n'
                        # f'RPC URL: \"{contract.network.rpc_url}\".\n'
                        f'From block: \"{from_block}\".'
                        f' To block: \"{last_block}\".'
                        f' Timeout: \"{timeout}\".'
                        f' Current block: \"{current_block_number}\".'
                        f'\nBlock range is too small. '
                        f'Min block range: \"{MIN_CONFIRMATION_BLOCK_COUNT}\".\n'
                    )
                )

                sleep(timeout)

                continue
            else:
                to_block = last_block
                timeout = DEFAULT_SCANNER_TIMEOUT

            info(
                SCANNER_INFO.format(
                    f'\nSCANNER: \"{self.name.upper()}\".\n'
                    # f'RPC URL: \"{contract.network.rpc_url}\".\n'
                    f'From block: \"{from_block}\".'
                    f' To block: \"{to_block}\".'
                    f' Timeout: \"{timeout}\".'
                    f' Current block: \"{current_block_number}\".'
                )
            )

            for _, event_name in enumerate(self._events):
                events = custom_rpc_provider.get_logs(
                    contract=contract,
                    event_name=event_name,
                    from_block=from_block,
                    to_block=to_block,
                )

                info(f'\"{event_name}\" events found: {len(events)}.')

                if not events:
                    continue

                for _, event in enumerate(events):
                    self._event_handlers.get(event_name)(
                        custom_rpc_provider,
                        contract,
                        event,
                    )

                continue

            last_proccessed_block = to_block

            sleep(timeout)

    def run(self):
        self.scan()


class NearScanner:
    data_object = 'crosschainTrades'

    def __init__(
        self,
        graphql_link: str,
        graphql_query: str,
        start_timestamp: str,
        network: str,
        contract: str,
        event_name: str,
        event_handlers: dict,
    ):
        self._graphql_link = graphql_link
        self._graphql_query = graphql_query
        self._start_timestamp = start_timestamp
        self._network = network
        self._contract = contract
        self._event_name = event_name
        self._event_handlers = event_handlers

    @auto_restart
    def scan(self):
        info(f"Scanning Near contract {self._contract} "
             f"with {self._graphql_link} from {self._start_timestamp}")

        current_timestamp = self._start_timestamp

        contract = Contract.objects.get(
            address__iexact=self._contract,
            network__title__iexact=self._network
        )

        rpc_provider = NearRpcProvider(contract.network.rpc_url_list[0])

        while 1:
            info(
                SCANNER_INFO.format(
                    f'\nSCANNER: \"{self._network.upper()}\".\n'
                    f'Start timestamp: \"{self._start_timestamp}\".'
                    f' Current timestamp: \"{current_timestamp}\".'
                )
            )

            payload = {
                'query': self._graphql_query,
                'variables': {
                    'start_timestamp': current_timestamp,
                },
            }

            result = send_post_request(
                url=self._graphql_link,
                payload=payload,
            )

            info(result)

            if not result or not result.get('data', {}).get(self.data_object):
                sleep(DEFAULT_SCANNER_TIMEOUT)
                continue

            event_list = result.get('data', {}).get(self.data_object)

            info(f"Near events found: {len(event_list)}")

            for event in event_list:
                event['transactionHash'] = event.get('id')

                self._event_handlers.get(self._event_name)(
                    rpc_provider,
                    contract,
                    AttributeDict(event),
                )

            current_timestamp = event_list[-1]['timestamp']

            sleep(DEFAULT_SCANNER_TIMEOUT_FAST)
