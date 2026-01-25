import uuid
from datetime import datetime
from database import get_connection, initialize_database


def add_task_to_queue(task_description="Rozmowa telefoniczna"):
    task_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO queue (id, status, created_at)
        VALUES (?, 'pending', ?)
        """,
        (task_id, created_at)
    )
    
    conn.commit()
    conn.close()

    print(f"Dodano zadanie do kolejki: {task_id}")
    return task_id


def add_multiple_tasks(count=100):
    print(f"Dodawanie {count} zadań do kolejki...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for i in range(1, count + 1):
        task_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        cursor.execute(
            """
            INSERT INTO queue (id, status, created_at)
            VALUES (?, 'pending', ?)
            """,
            (task_id, created_at)
        )
        
        if i % 10 == 0:
            print(f"Postęp: {i}/{count}")
    
    conn.commit()
    conn.close()
    
    print(f"\nDodano {count} zadań do kolejki!")


if __name__ == "__main__":
    initialize_database()

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
