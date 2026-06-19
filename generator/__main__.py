import sys

from loguru import logger

from generator.main import main_program

if __name__ == "__main__":
    try:
        main_program()
    except KeyboardInterrupt:
        logger.warning("SIGINT received. Terminating application...")
        sys.exit(0)
    except Exception as exc:
        logger.error(f"{exc.__class__.__name__}: {str(exc)}")
        sys.exit(-1)
    else:
        sys.exit(0)
