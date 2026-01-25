import os
from collections import Counter
from database import get_connection, initialize_database, dict_from_row, DATABASE_FILE


def read_queue():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM queue ORDER BY created_at ASC")
    rows = cursor.fetchall()
    
    conn.close()
    
    return [dict_from_row(row) for row in rows]


def display_stats():
    tasks = read_queue()

    if not tasks:
        print("Kolejka jest pusta!")
        return

    status_counts = Counter(task["status"] for task in tasks)

    print(f"Całkowita liczba zadań: {len(tasks)}")
    print(f"Oczekujące (pending): {status_counts.get('pending', 0)}")
    print(f"W trakcie (in_progress): {status_counts.get('in_progress', 0)}")
    print(f"Zakończone (done): {status_counts.get('done', 0)}")

    consumers = set(task["consumer_id"] for task in tasks if task["consumer_id"])
    if consumers:
        print(f"\nLiczba aktywnych consumerów: {len(consumers)}")
        print("Consumers:", ", ".join(consumers))

    in_progress = [t for t in tasks if t["status"] == "in_progress"]
    if in_progress:
        print("\nZadania w trakcie realizacji:")
        for task in in_progress:
            print(f"  - {task['id'][:8]}... (Consumer: {task['consumer_id']})")

    if len(tasks) > 0:
        done_percentage = (status_counts.get("done", 0) / len(tasks)) * 100
        print(f"\nPostęp: {done_percentage:.1f}%")

        bar_length = 40
        filled = int(bar_length * done_percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"[{bar}] {done_percentage:.1f}%")


def clear_queue():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM queue")
    
    conn.commit()
    conn.close()
    
    print("Kolejka wyczyszczona!")


def drop_database():
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print("Baza danych usunięta!")
    else:
        print("Baza danych nie istnieje!")


if __name__ == "__main__":
    initialize_database()
    
    print("Wybierz opcję:")
    print("1. Pokaż statystyki")
    print("2. Wyczyść kolejkę (usuń wszystkie zadania)")
    print("3. Usuń bazę danych")

    choice = input("\nTwój wybór (1/2/3): ").strip()

    if choice == "1":
        display_stats()
    elif choice == "2":
        confirm = (
            input("Czy na pewno chcesz wyczyścić kolejkę? (tak/nie): ").strip().lower()
        )
        if confirm == "tak":
            clear_queue()
        else:
            print("Anulowano.")
    elif choice == "3":
        confirm = (
            input("Czy na pewno chcesz usunąć bazę danych? (tak/nie): ").strip().lower()
        )
        if confirm == "tak":
            drop_database()
        else:
            print("Anulowano.")
    else:
        print("Nieprawidłowy wybór!")
