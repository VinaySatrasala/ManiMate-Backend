import threading
import logging
from time import sleep
from app.services.memory_manager import MemoryManager

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class SyncService:
    def __init__(self, memory_manager: MemoryManager, sync_interval: int = 300):
        self.memory_manager = memory_manager
        self.sync_interval = sync_interval  # seconds
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def _sync_worker(self):
        """Background worker for periodic syncing."""
        while self.running:
            try:
                with self.lock:
                    logger.info("Starting periodic sync from Redis to PostgreSQL...")
                    self.memory_manager.sync_redis_to_postgres()
                    logger.info("Periodic sync completed successfully.")
            except Exception as e:
                logger.error(f"Periodic sync error: {e}")
            sleep(self.sync_interval)

    def start(self):
        """Start the periodic sync service."""
        if self.running:
            logger.warning("Sync service already running.")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.thread.start()
        logger.info(f"Sync service started (interval: {self.sync_interval}s)")

    def stop(self):
        """Stop the periodic sync service."""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Sync service stopped.")

    def sync_now(self):
        """Trigger an immediate sync."""
        try:
            with self.lock:
                logger.info("Starting manual sync from Redis to PostgreSQL...")
                self.memory_manager.sync_redis_to_postgres()
                logger.info("Manual sync completed successfully.")
        except Exception as e:
            logger.error(f"Manual sync error: {e}")
