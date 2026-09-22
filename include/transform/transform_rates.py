import json
from pathlib import Path
import logging

logger=logging.getLogger(__name__)

def transform_exchange_rates(input_file,output_file,ds):

    with open(input_file) as f:
        data=json.load(f)   #json-python obj

    base_currency=data["base_code"]
    source_timestamp=data["time_last_update_utc"]
    rates=data["rates"]

    transformed_data = []   #Because we're going to keep adding one record at a time.
    total_records = len(rates)
    valid_records = 0
    none_rates = 0
    invalid_type = 0
    invalid_rate = 0

    for currency,rate in rates.items():
        if rate is None:
            none_rates +=1
            #print(f"Skipping {currency}: rate is None")
            logger.warning(f"Skipping {currency}: rate is None")
            continue
        if not isinstance(rate, (int, float)):
            invalid_type +=1
            #print(f"Skipping {currency}: invalid rate {rate}")
            logger.warning(f"Skipping {currency}: invalid rate {rate}")
            continue
        if rate <= 0:
            invalid_rate +=1
            #print(f"Skipping {currency}: invalid exchange rate {rate}")
            logger.warning(f"Skipping {currency}: invalid exchange rate {rate}")
            continue
        record = {
            "load_date":ds,
            "source_timestamp":source_timestamp,
            "base_currency":base_currency,
            "target_currency":currency,
            "exchange_rate":rate
        }

        transformed_data.append(record)
        valid_records +=1

    # -----------------------------
    # Transform Summary
    # -----------------------------
    logger.info("=========Transform Summary ===========")
    logger.info(f"Total Records      : {total_records}")
    logger.info(f"Valid Records      : {valid_records}")
    logger.info(f"Skipped (None)     : {none_rates}")
    logger.info(f"Skipped (Type)     : {invalid_type}")
    logger.info(f"Skipped (<= 0)     : {invalid_rate}")

    logger.info("=====================================")
    logger.info(f"Successfully transformed {len(transformed_data)} records.")

    if not transformed_data:
        raise ValueError("No valid exchange rates found after transformation.")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True,exist_ok=True)

    with open(output_path,"w") as f:
        json.dump(transformed_data,f,indent=2)

    return str(output_path)

    


    