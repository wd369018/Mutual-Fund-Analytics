"""
Master ETL Pipeline - Mutual Fund Analytics

This script runs the complete ETL process by calling the existing
data_ingestion.py module.

Run from the project root:

    python scripts/etl_pipeline.py
"""

from pathlib import Path
import logging
import sys


# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

# Make sure scripts/ can be imported when this file is executed directly.
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Import existing ingestion pipeline
# -------------------------------------------------------------------

try:
    from data_ingestion import main as run_data_ingestion
except ImportError as exc:
    logger.error("Could not import data_ingestion.py: %s", exc)
    sys.exit(1)


# -------------------------------------------------------------------
# ETL Pipeline
# -------------------------------------------------------------------

def main():
    """
    Run the complete ETL pipeline.

    The existing data_ingestion.py performs the actual data ingestion
    and cleaning work. This file acts as the master entry point so
    the complete process can be executed with one command.
    """

    logger.info("=" * 60)
    logger.info("MUTUAL FUND ANALYTICS - ETL PIPELINE")
    logger.info("=" * 60)

    logger.info("Project directory: %s", BASE_DIR)

    try:
        # -----------------------------------------------------------
        # Step 1: Run data ingestion
        # -----------------------------------------------------------
        logger.info("Step 1/1: Starting data ingestion...")

        run_data_ingestion()

        logger.info("Data ingestion completed successfully.")

        # -----------------------------------------------------------
        # Pipeline completed
        # -----------------------------------------------------------
        logger.info("=" * 60)
        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

    except FileNotFoundError as exc:
        logger.error("Required file or directory not found.")
        logger.error("%s", exc)
        raise

    except PermissionError as exc:
        logger.error("Permission denied while accessing a file.")
        logger.error("%s", exc)
        raise

    except Exception as exc:
        logger.exception("ETL pipeline failed.")
        logger.error("Error: %s", exc)
        raise


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        logger.warning("ETL pipeline interrupted by user.")
        sys.exit(130)

    except Exception:
        logger.error("ETL pipeline terminated with errors.")
        sys.exit(1)