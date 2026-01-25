import csv
import time
import os
from datetime import datetime
import sys
import uuid

QUEUE_FILE = "queue.csv"

TASK_DURATION = 30

CHECK_INTERVAL = 5


class Consumer:
    def __init__(self, consumer_id=None):
        self.consumer_id = consumer_id or str(uuid.uuid4())[:8]
        print(f"Consumer {self.consumer_id} uruchomiony!")

    def read_queue(self):
        if not os.path.exists(QUEUE_FILE):
            return []

        with open(QUEUE_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def write_queue(self, tasks):
        if not tasks:
            return

        with open(QUEUE_FILE, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "id",
                "status",
                "created_at",
                "started_at",
                "completed_at",
                "consumer_id",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tasks)

    def find_pending_task(self, tasks):
        for i, task in enumerate(tasks):
            if task["status"] == "pending":
                return i
        return None

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

    def process_queue(self):
        tasks = self.read_queue()

        if not tasks:
            return False

        pending_index = self.find_pending_task(tasks)

        if pending_index is None:
            return False

        task = tasks[pending_index]

        task["status"] = "in_progress"
        task["started_at"] = datetime.now().isoformat()
        task["consumer_id"] = self.consumer_id

        self.write_queue(tasks)

        self.execute_task(task)

        tasks = self.read_queue()

        for t in tasks:
            if t["id"] == task["id"]:
                t["status"] = "done"
                t["completed_at"] = datetime.now().isoformat()
                break

        self.write_queue(tasks)

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
    consumer_id = sys.argv[1] if len(sys.argv) > 1 else None

    print("CONSUMER\n")
    consumer = Consumer(consumer_id)
    consumer.run()
