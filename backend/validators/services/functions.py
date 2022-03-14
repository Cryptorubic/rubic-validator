from logging import exception, info
from django.db import transaction

from django.db.utils import OperationalError

from contracts.exceptions import (
    ContractTransactionAlreadyProcessed,
    ContractTransactionAlreadyReverted,
)
from contracts.models import Contract
from contracts.services.functions import _check_is_processed_transaction
from backend.consts import NETWORK_NAMES
from ..models import ValidatorSwap


def process_swap(swap_id):
    """
    Process validator swap depends on it's status
    """

    info('check swap')
    try:
        with transaction.atomic():
            swap = ValidatorSwap.displayed_objects.select_for_update(
                nowait=True
            ) \
                .filter(id=swap_id) \
                .first()

    except OperationalError:
        exception('swap model locked')

        return

    try:
        to_contract = Contract.get_contract_by_blockchain_id(
            swap.transaction.data.get('params', [1])[0],
        )

        if to_contract.network.title not in (
            NETWORK_NAMES.get('solana'),
            NETWORK_NAMES.get('near'),
        ):
            _check_is_processed_transaction(
                Contract.get_contract_by_blockchain_id(
                    swap.transaction.data.get('params', [1])[0]
                ),
                swap.transaction.event_data.get('transactionHash'),
                '',
            )
    except (
        ContractTransactionAlreadyProcessed,
        ContractTransactionAlreadyReverted
    ):
        swap.status = ValidatorSwap.STATUS_SIGNATURE_SEND
        swap.save()

    if swap.status == ValidatorSwap.STATUS_SIGNATURE_CREATED:
        swap.send_signature_to_relayer()

    return
