import json
import logging

logger=logging.getLogger(__name__)

def check_data_quality(processed_file):
    logger.info("Starting data quality checks.")

    with open(processed_file, "r") as f:
        data=json.load(f)

        #Dataset must not be empty
        if not data:
            logger.error("Data quality check failed: No data found.")
            raise ValueError("Processed dataset is empty.")

        logger.info(f"Dataset contains {len(data)} records.")

        #Detect Duplicate Currency Pairs
        #use python set-set stores only the unique values

        seen = set()

        for record in data:
            #duplicate check
            currency_pair = (
                record["base_currency"],
                record["target_currency"]
            )

            if currency_pair in seen:
                logger.error(
                    f"Duplicate currency pair found :{currency_pair}"
                )
                raise ValueError(
                    f"Duplicate currency pair: {currency_pair}"
                )
            seen.add(currency_pair)
        
            #Exchange rate must be greater than zero
        
            exchange_rate=record["exchange_rate"]

            if exchange_rate <= 0:
                logger.error(
                    f"Invalid exchane rate found for {record["target_currency"]} :{exchange_rate}"
                )
                raise ValueError(
                    f" Invalid exchange rate for {record["target_currecny"]}:{exchange_rate}"
                )
            
        logger.info("No duplicate currency pairs  found.")
        logger.info("All exchange rates are valid.")

        #completeness check -did i receive enough data
        MINIMUM_EXPECTED_CURRENCIES=100

        if len(data) < MINIMUM_EXPECTED_CURRENCIES:
            logger.error(f"Expected at least {MINIMUM_EXPECTED_CURRENCIES} currencies," f"but found only  {len(data)}")
            raise ValueError(f"Insufficient currency records:{len(data)}")
        logger.info("Completeness check passed.")
        logger.info(f"Data quality check completed successfully.")