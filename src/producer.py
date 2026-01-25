import csv
import uuid
import os
from datetime import datetime
from pathlib import Path

QUEUE_FILE = "queue.csv"


def initialize_queue_file():
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "status",
                    "created_at",
                    "started_at",
                    "completed_at",
                    "consumer_id",
                ]
            )


def add_task_to_queue(task_description="Rozmowa telefoniczna"):
    task_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    with open(QUEUE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([task_id, "pending", created_at, "", "", ""])

    print(f"Dodano zadanie do kolejki: {task_id}")
    return task_id


def add_multiple_tasks(count=100):
    print(f"Dodawanie {count} zadań do kolejki...")
    for i in range(1, count + 1):
        add_task_to_queue(f"Rozmowa telefoniczna #{i}")
        if i % 10 == 0:
            print(f"Postęp: {i}/{count}")
    print(f"\nDodano {count} zadań do kolejki!")


if __name__ == "__main__":
    initialize_queue_file()

    print("Wybierz opcję:")
    print("1. Dodaj jedno zadanie")
    print("2. Dodaj 100 zadań")
    print("3. Dodaj N zadań (własna liczba)")

    choice = input("\nTwój wybór (1/2/3): ").strip()

    if choice == "1":
        add_task_to_queue()
    elif choice == "2":
        add_multiple_tasks(100)
    elif choice == "3":
        try:
            count = int(input("Ile zadań dodać? "))
            add_multiple_tasks(count)
        except ValueError:
            print("Błąd: Podaj prawidłową liczbę!")
    else:
        print("Nieprawidłowy wybór!")
