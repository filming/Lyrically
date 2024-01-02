import logging
import os

from lyrically import Lyrically

LOGS_DIR_PATH = f"../storage/logs"

if not os.path.exists(LOGS_DIR_PATH): os.mkdir(LOGS_DIR_PATH)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{LOGS_DIR_PATH}/main.log", "w")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)

def main():
    logger.info("Program has started!")

    lyrically = Lyrically(use_proxies = False)
    lyrically.setup()

    artist_name = "Sabrina Carpenter"
    lyrically.get_artist_songs(artist_name)

if __name__ == "__main__":
    main()
