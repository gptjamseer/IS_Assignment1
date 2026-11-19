import Task1
import Task2
import Task3
import Task4


def main():
    while True:
        choice = input("Select a task (1-4, q/end/quit to exit): ").strip().lower()
        if choice in ("q", "end", "quit"):
            break
        if choice == "1":
            Task1.main()
        elif choice == "2":
            Task2.main()
        elif choice == "3":
            Task3.main()
        elif choice == "4":
            Task4.main()
        else:
            print("Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
