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
    from contracts.services.scanners.functions import start_near_scanner

    start_near_scanner(
        scanner={
            'contract_address': 'multichain.rubic-finance.near',
            'graphql_link': 'https://api.thegraph.com/subgraphs/name/realhum/near-subgraph',
            'graphql_query': """
                    query LatestTrades($start_timestamp: String) {
                      crosschainTrades(
                        where: {timestamp_gt: $start_timestamp},
                        orderBy: timestamp
                      ) {
                        id
                        wallet {
                          id
                        }
                        timestamp
                        blockHash
                      }
                    }
                """,
            'start_timestamp': '1643188709949243217',
        }
    )
