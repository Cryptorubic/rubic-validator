from web3.datastructures import AttributeDict

from base.tests import BaseTestCase
from contracts.models import Contract
from networks.models import Network, CustomRpcProvider

from .models import ValidatorSwap


class ValidatorTestCase(BaseTestCase):
    def test_validator_swap_create(self):
        rpc_provider = CustomRpcProvider(
            Network.displayed_objects.get(
                title__iexact='binance-smart-chain',
            )
        )
        contract = Contract.get_contract_by_blockchain_id(1)

        ValidatorSwap.create_swap(
            rpc_provider=rpc_provider,
            contract=contract,
            txn_hash=self.transaction_hash,
            event=self.event_data,
        )

        validator_swap = ValidatorSwap.displayed_objects.get(
            transaction__hash__iexact=self.transaction_hash,
        )

        self.assertEqual(
            validator_swap.transaction.event_data['transactionHash'],
            self.transaction_hash,
            "create_swap doesn't saved ValidatorSwap correctly",
        )

    def test_send_signature_to_relayer(self):
        rpc_provider = CustomRpcProvider(
            Network.displayed_objects.get(
                title__iexact='binance-smart-chain',
            )
        )
        contract = Contract.get_contract_by_blockchain_id(1)

        validator_swap = ValidatorSwap.create_swap(
            rpc_provider=rpc_provider,
            contract=contract,
            txn_hash=self.transaction_hash,
            event=self.event_data,
        )

        validator_swap.signature = self.signature

        validator_swap.send_signature_to_relayer()

        self.assertEqual(
            validator_swap.status,
            ValidatorSwap.STATUS_SIGNATURE_SEND,
            "signature wasn't send",
        )
