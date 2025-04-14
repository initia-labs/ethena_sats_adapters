import logging
from typing import Dict, List, Optional
from constants.chains import Chain
from constants.summary_columns import SummaryColumn
from constants.example_integrations import INITIA_SUSDE_START_BLOCK
from integrations.integration_ids import IntegrationID
from integrations.l2_delegation_integration import L2DelegationIntegration
from utils.request_utils import requests_retry_session

INITIA_ENDPOINT = "https://ethena-api.initia.xyz/balances"

class InitiaIntegration(L2DelegationIntegration):
    def __init__(
        self,
        integration_id: IntegrationID,
        start_block: int,
        chain: Chain = Chain.INITIA,
        reward_multiplier: int = 30,
        end_block: Optional[int] = None,
    ):
        super().__init__(
            integration_id=integration_id,
            start_block=start_block,
            chain=chain,
            summary_cols=[SummaryColumn.INITIA_SHARDS],
            reward_multiplier=reward_multiplier,
            end_block=end_block,
        )
    
    def get_l2_block_balances(
        self,
        cached_data: Dict[int, Dict[str, float]],
        blocks: List[int],
    ) -> Dict[int, Dict[str, float]]:
        logging.info(
            f"Getting block data for Initia integration example at blocks {blocks}..."
        )

        data_per_block: Dict[int, Dict[str, float]] = {}

        for target_block in blocks:
            if self.start_block > target_block or (
                self.end_block and target_block > self.end_block
            ):
                data_per_block[target_block] = {}
                continue
            data_per_block[target_block] = self.get_participants_data(target_block)
        
        return data_per_block

    def get_participants_data(self, block: int) -> Dict[str, float]:
        logging.info(
            f"Fetching participants data for Initia integration example at block {block}..."
        )
        participants_data: Dict[str, float] = {}

        while True:
            try:
                res = requests_retry_session().get(
                    INITIA_ENDPOINT,
                    params={"block": block},
                    timeout=60,
                )
                participants_data = res.json()
            except Exception as e:
                err_msg = f"Error getting participants data for Initia integration example: {e}"
                logging.error(err_msg)
                slack_message(err_msg)
                break

        return participants_data

if __name__ == "__main__":
    example_integration = InitiaIntegration(
        integration_id=IntegrationID.INITIA_SUSDE_LP,
        start_block=INITIA_SUSDE_START_BLOCK
    )

    example_integration_output = example_integration.get_l2_block_balances(
        cached_data={},
        blocks=list(range(INITIA_SUSDE_START_BLOCK, INITIA_SUSDE_START_BLOCK + 10000, 100)),
    )

    print("=" * 120)
    print("Run without cached data", example_integration_output)
    print("=" * 120, "\n" * 5)
