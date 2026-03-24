from pipeline import run_pipeline
from live_pipeline import run_live_pipeline

print("Choose Mode")
print("1. Recorded Audio")
print("2. Live Meeting")

choice = input("Enter choice: ")

if choice == "1":
    run_pipeline()

elif choice == "2":
    run_live_pipeline()

else:
    print("Invalid choice")