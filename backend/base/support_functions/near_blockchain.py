import base58
import base64
import json

from backend.consts import SUPPORT_FUNCTIONS_DICT
from networks.services.functions import convert_to_ethereum_like_address


def parce_near_receipt(receipt: dict):
    decoded_data = json.loads(
        bytes.decode(
            base64.b64decode(
                receipt['receipt']['Action']['actions'][0]['FunctionCall'][
                    'args']
            ),
            'utf-8',
        )
    )

    receipt_data = json.loads(decoded_data['msg'])

    amount = int(decoded_data['amount'])

    event_data = receipt_data.get('SwapTokensToOther')

    if not event_data:
        event_data = receipt_data.get('SwapTransferTokensToOther')
        action_data = {
            'token_in': receipt['predecessor_id'],
            'token_out': receipt['predecessor_id'],
            'amount_in': amount,
            'min_amount_out': amount,
        }
    else:
        action_data = event_data.get('swap_actions', [])[0]

    params = event_data.get('swap_to_params', {})

    converted_receipt_id = base58.b58decode(receipt.get('receipt_id', ))[:32].hex()

    second_path = [
        convert_to_ethereum_like_address(address)
        for address in params.get('second_path', [])
    ]

    transaction_data = {
        "params": [
            int(params.get('blockchain')),
            int(action_data.get('amount_in')),
            [
                action_data.get('token_in'),
                action_data.get('token_out'),
            ],
            second_path,
            int(action_data.get('min_amount_out')),
            int(params.get('min_amount_out')),
            params.get('new_address'),
            False,
            False,
            '',
            SUPPORT_FUNCTIONS_DICT.get(
                f"0x{params.get('signature')}"
            ),
        ]
    }

    event_data = {
        "args": {
            "path": second_path,
            "blockchain": int(params.get('blockchain')),
            "newAddress": params.get('new_address'),
            "RBCAmountIn": int(action_data.get('min_amount_out')),
            "amountSpent": int(params.get('min_amount_out')),
        },
        "event": 'TransferTokensToOtherBlockchainUser',
        "transactionHash": f"0x{converted_receipt_id}",
    }

    return transaction_data, event_data
