"""
Master execution script for the Mutual Fund Analytics project.

This script runs the main project pipeline in sequence.
"""

import logging

from scripts.data_ingestion import main as run_ingestion


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


def main():
    """Run the complete Mutual Fund Analytics pipeline."""

    logging.info("Starting Mutual Fund Analytics pipeline.")

    run_ingestion()

    logging.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()