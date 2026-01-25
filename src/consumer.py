import time
import sys
import uuid
from datetime import datetime
from database import get_connection, initialize_database, dict_from_row

TASK_DURATION = 30
CHECK_INTERVAL = 5


class Consumer:
    def __init__(self, consumer_id=None):
        self.consumer_id = consumer_id or str(uuid.uuid4())[:8]
        print(f"Consumer {self.consumer_id} uruchomiony!")

    def find_and_claim_pending_task(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT * FROM queue 
            WHERE status = 'pending' 
            ORDER BY created_at ASC 
            LIMIT 1
            """
        )
        task = cursor.fetchone()
        
        if task is None:
            conn.close()
            return None
        
        task_dict = dict_from_row(task)
        task_id = task_dict["id"]
        started_at = datetime.now().isoformat()
        
        cursor.execute(
            """
            UPDATE queue 
            SET status = 'in_progress', 
                started_at = ?, 
                consumer_id = ?
            WHERE id = ? AND status = 'pending'
            """,
            (started_at, self.consumer_id, task_id)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            return None
        
        conn.commit()
        conn.close()
        
        task_dict["status"] = "in_progress"
        task_dict["started_at"] = started_at
        task_dict["consumer_id"] = self.consumer_id
        
        return task_dict

    def execute_task(self, task):
        task_id = task["id"]
        print(f"\n[{self.consumer_id}] Rozpoczynam wykonywanie zadania: {task_id}")
        print(f"[{self.consumer_id}] Szacowany czas: {TASK_DURATION}s")

        for i in range(0, TASK_DURATION, 5):
            time.sleep(5)
            remaining = TASK_DURATION - i - 5
            if remaining > 0:
                print(f"[{self.consumer_id}] Pozostało: {remaining}s")

        print(f"[{self.consumer_id}] Zadanie zakończone: {task_id}")

    def complete_task(self, task_id):
        conn = get_connection()
        cursor = conn.cursor()
        
        completed_at = datetime.now().isoformat()
        
        cursor.execute(
            """
            UPDATE queue 
            SET status = 'done', 
                completed_at = ?
            WHERE id = ?
            """,
            (completed_at, task_id)
        )
        
        conn.commit()
        conn.close()

    def process_queue(self):
        task = self.find_and_claim_pending_task()

        if task is None:
            return False

        self.execute_task(task)
        self.complete_task(task["id"])

        return True

    def run(self):
        print(f"[{self.consumer_id}] Sprawdzam kolejkę co {CHECK_INTERVAL}s...\n")

        try:
            while True:
                processed = self.process_queue()

                if not processed:
                    print(
                        f"[{self.consumer_id}] Brak zadań w kolejce, czekam {CHECK_INTERVAL}s..."
                    )
                    time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n[{self.consumer_id}] Consumer zatrzymany przez użytkownika")
            sys.exit(0)


if __name__ == "__main__":
    initialize_database()
    
    consumer_id = sys.argv[1] if len(sys.argv) > 1 else None

    print("CONSUMER\n")
    consumer = Consumer(consumer_id)
    consumer.run()
