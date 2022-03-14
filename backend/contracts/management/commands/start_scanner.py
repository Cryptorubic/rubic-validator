from typing import Any, Optional

from django.core.management.base import BaseCommand

from ...services.scanners.functions import start_scanners


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        start_scanners(
            scanners={
                'binance-smart-chain': {
                    'network': 'binance-smart-chain',
                    'contract_address': '',
                    'start_block': None,
                },
                'polygon': {
                    'network': 'polygon',
                    'contract_address': '',
                    'start_block': None,
                },
            }
        )
