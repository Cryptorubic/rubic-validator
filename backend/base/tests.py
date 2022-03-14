from django.test import TestCase, override_settings
from web3.datastructures import AttributeDict

from backend.consts import FULL_ABI
from contracts.models import Contract
from networks.models import Network


@override_settings(
    VALIDATOR_PRIVATE_KEY=(
        "e7f76474dcedbd059dfa63c0bcf1ea2d93af0927d7363e6df8a726477d15fd06"
    )
)
class BaseTestCase(TestCase):
    hash_packed = '8b10519074b9133715ce92e265cc1699ce6e066648e68c65fcc7fe933cfc6a5d'
    signature = 'c8bc02a7bb63778aa3f4a39da50ca5c4444a50736b1d15fea61317c387ad94d65c16336643705748a5a1171f923c91aeee0155be4cf8c793694f334b2b8598cc1b'
    transaction_hash = "0x6f3814ca9fc864d8ac18759ceba73db4378ceeb4db26080946fe5cfe23e49ccf"
    wallet_address = '0xaad76212aff4f81be59b1d0134c498573109409d'
    token_amount = 111514022
    blockchain_id = 2
    event_data = AttributeDict({
        "args": AttributeDict({
            "provider": "0x0000000000000000000000000000000000000000",
            "RBCAmountIn": 111514022390579475349,
            "amountSpent": 111514022390579475349
        }),
        "event": "TransferCryptoToOtherBlockchainUser",
        "address": "0x70e8C8139d1ceF162D5ba3B286380EB5913098c4",
        "logIndex": 259,
        "blockHash": "0xf59401254d9386453da5035b5535d2837bcc255ed607fe0bdc86af03faa0d3e2",
        "blockNumber": 15963554,
        "transactionHash": "0x6f3814ca9fc864d8ac18759ceba73db4378ceeb4db26080946fe5cfe23e49ccf",
        "transactionIndex": 81
    })

    def setUp(self):
        bsc_network = Network.displayed_objects.create(
            title='binance-smart-chain',
            rpc_url_list=[
                "https://bsc-dataseed.binance.org/",
            ],
        )
        eth_network = Network.displayed_objects.create(
            title='ethereum',
            rpc_url_list=[
                "https://api.mycryptoapi.com/eth",
                "https://rpc.flashbots.net/",
                "https://eth-mainnet.gateway.pokt.network/v1/5f3453978e354ab992c4da79",
            ],
        )

        Contract.displayed_objects.create(
            title='RUBIC_SWAP_CONTRACT_IN_BSC_PROD_READY',
            type=Contract.TYPE_CROSSCHAIN_ROUTING,
            address='0x70e8C8139d1ceF162D5ba3B286380EB5913098c4',
            network=bsc_network,
            hash_of_creation='0x9902f3cf707ce064d17b4c2368c8f6b2551a70943f7c3429321842e9d2c55dcf',
            blockchain_number=1,
            abi=FULL_ABI,
        )
        Contract.displayed_objects.create(
            title='RUBIC_SWAP_CONTRACT_IN_ETH_PROD_READY',
            type=Contract.TYPE_CROSSCHAIN_ROUTING,
            address='0xD8b19613723215EF8CC80fC35A1428f8E8826940',
            network=eth_network,
            hash_of_creation='0xcb99d1cc4ee13668087c2f8fcbe3c1f0b6a1e9bc682026fd03ffad5bda882843',
            blockchain_number=2,
            abi=FULL_ABI,
        )
