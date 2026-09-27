from pathlib import Path
from datetime import datetime,timedelta
import logging

logger=logging.getLogger(__name__)

def purge_old_files(directory,retention_days,ds):
     """
     Deletes JSON files older than the retention period.

     Parameters
     ----------
     directory : str
        Directory containing dated JSON files.
     retention_days : int
        Number of days to keep.
     """

     directory = Path(directory)
     if not directory.exists():
        logger.warning(f"Directory doesnt exists: {directory}")
        return

     execution_date= datetime.strptime(ds, "%Y-%m-%d").date()
     #timedelta represents a duration or time difference,lets you add or subtract days, hours ,minutes from date or time
     cutoff_date=execution_date - timedelta(days=retention_days)
     deleted_files = 0
     kept_files = 0

     #go through every json file
     for file in directory.glob("*.json"):
         try:
             #filename example:2026-09-27.json  -- file.stem-removes.json
             file_date=datetime.strptime(file.stem, "%Y-%m-%d").date()  # datetime.strptime--converts that text into a real date python can compare
             if file_date < cutoff_date:
                 file.unlink() #delete if condition is true
                 deleted_files += 1
                 logger.info(f"Deleted old file: {file.name}")

             else:
                 kept_files += 1
         except ValueError:
             logger.warning(f"Skipping file with invalid name: {file.name}")

     logger.info("==========Retention Summary ===========")
     logger.info(f"Directory            : {directory}")
     logger.info(f"Execution Date : {execution_date}")
     logger.info(f"Cutoff Date    : {cutoff_date}")
     logger.info(f"Retention Days       : {retention_days}")
     logger.info(f"Deleted files        : {deleted_files}")
     logger.info(f"Kept files           : {kept_files}")

     logger.info("========================================")

