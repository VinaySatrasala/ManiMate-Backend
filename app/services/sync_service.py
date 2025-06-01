# sync_service.py
import threading
from time import sleep
from app.services.memory_manager import MemoryManager

class SyncService:
    def __init__(self, memory_manager: MemoryManager, sync_interval: int = 300):
        self.memory_manager = memory_manager
        self.sync_interval = sync_interval  # seconds
        self.running = False
        self.thread = None
    
    def _sync_worker(self):
        """Background worker for periodic syncing"""
        while self.running:
            try:
                self.memory_manager.sync_redis_to_postgres()
            except Exception as e:
                print(f"Sync error: {e}")
            sleep(self.sync_interval)
    
    def start(self):
        """Start the periodic sync service"""
        if self.running:
            print("Sync service already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.thread.start()
        print(f"Sync service started (interval: {self.sync_interval}s)")
    
    def stop(self):
        """Stop the periodic sync service"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Sync service stopped")
    
    def sync_now(self):
        """Trigger an immediate sync"""
        self.memory_manager.sync_redis_to_postgres()