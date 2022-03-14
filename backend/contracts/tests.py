from web3.datastructures import AttributeDict

from base.tests import BaseTestCase
from contracts.services.functions import _get_signature
from contracts.services.scanners.handlers import create_signature_transfer_tokens_handler
from networks.models import CustomRpcProvider, Network
from validators.models import ValidatorSwap
from .models import Contract


class ContractTestCase(BaseTestCase):
    def test_get_contract_by_blockchain_id(self):
        contract_address = '0x70e8C8139d1ceF162D5ba3B286380EB5913098c4'

        contract = Contract.get_contract_by_blockchain_id(1)

        self.assertEqual(
            contract.address,
            contract_address,
            'get_contract_by_blockchain_id return incorrect contract',
        )

    def test_hash_packed(self):
        contract = Contract.get_contract_by_blockchain_id(1)

        self.assertEqual(
            contract.get_hash_packed(
                address=self.wallet_address,
                token_amount_with_fee=self.token_amount,
                original_txn_hash=self.transaction_hash,
                blockchain_id=self.blockchain_id,
            ).hex(),
            self.hash_packed,
            'get_hash_packed method returned incorrect hash',
        )

    def test_get_signature(self):
        self.assertEqual(
            _get_signature(
                original_txn_hash=self.transaction_hash,
                blockchain_id=self.blockchain_id,
                new_address=self.wallet_address,
                transit_token_amount_in=self.token_amount,
            ),
            self.signature,
            '_get_signature function returned incorrect signature',
        )

    def test_create_signature(self):
        rpc_provider = CustomRpcProvider(
            Network.displayed_objects.get(
                title__iexact='binance-smart-chain',
            )
        )
        contract = Contract.get_contract_by_blockchain_id(1)

        create_signature_transfer_tokens_handler(
            rpc_provider=rpc_provider,
            contract=contract,
            event=self.event_data,
        )

        validator_swap = ValidatorSwap.displayed_objects.get(
            transaction__hash__iexact=self.transaction_hash,
        )

        self.assertEqual(
            validator_swap.signature,
            self.signature,
        )
