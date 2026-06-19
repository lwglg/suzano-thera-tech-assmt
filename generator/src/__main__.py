import os

from loguru import logger

from src.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("SIGINT received. Terminating application...")
        os.exit(0)
    except Exception as exc:
        logger.error(f"{exc.__class__.__name__}: {str(exc)}")
        os.exit(-1)
    else:
        os.exit(0)
