
import os
import random
import re
import threading
import time
from datetime import datetime, timedelta

LOG_FILE = "lottery_log.txt"
USERS_FILE = "registered_users.txt"
REGISTRATION_DURATION = 3600
EXTENSION_DURATION = 1800
SAVE_INTERVAL = 300
UPDATE_INTERVAL = 600
MIN_USERS = 5

users = set()
start_time = datetime.now()
registration_end_time = start_time + timedelta(seconds=REGISTRATION_DURATION)
extended = False
lock = threading.Lock()

def is_valid_username(username):
    return bool(re.match(r"^[a-zA-Z0-9_]+$", username))

def save_progress():
    with lock:
        with open(USERS_FILE, 'w') as f:
            for user in users:
                f.write(user + "\n")

def log_event(message):
    with open(LOG_FILE, 'a') as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def auto_save():
    while datetime.now() < registration_end_time:
        time.sleep(SAVE_INTERVAL)
        save_progress()
        log_event("Auto-saved user list.")

def time_remaining_alert():
    while datetime.now() < registration_end_time:
        time.sleep(UPDATE_INTERVAL)
        remaining = (registration_end_time - datetime.now()).seconds
        print(f"\n⏳ Time remaining for registration: {remaining // 60} minutes\n")

def registration_phase():
    print("🎟️ Welcome to the Terminal-Based Lottery System!")
    print("Registration is open for 1 hour. Enter unique usernames to participate.")
    print("Enter 'exit' to stop early.")

    threading.Thread(target=auto_save, daemon=True).start()
    threading.Thread(target=time_remaining_alert, daemon=True).start()

    while datetime.now() < registration_end_time:
        username = input("Enter a unique username: ").strip()
        if username.lower() == 'exit':
            break
        if not is_valid_username(username):
            print("❌ Invalid username. Use only letters, numbers, and underscores.")
            continue
        with lock:
            if username in users:
                print("⚠️ Username already taken.")
            else:
                users.add(username)
                log_event(f"User registered: {username}")
                print(f"✅ Registered: {username} | Total Users: {len(users)}")

    save_progress()

def lottery_draw():
    global registration_end_time, extended

    if len(users) < MIN_USERS and not extended:
        print("\n⚠️ Less than 5 users registered. Extending registration by 30 minutes...")
        log_event("Extended registration due to low participation.")
        extended = True
        registration_end_time += timedelta(seconds=EXTENSION_DURATION)
        registration_phase()
        lottery_draw()
        return

    if len(users) == 0:
        print("❌ No users registered. Lottery closed.")
        log_event("No participants. Program exited.")
        return

    winner = random.choice(list(users))
    log_event(f"🎉 Winner Selected: {winner}")
    print("\n🎊 LOTTERY WINNER ANNOUNCEMENT 🎊")
    print("=====================================")
    print(f"🏆 Winner: {winner}")
    print(f"👥 Total Participants: {len(users)}")
    print("=====================================")

if __name__ == "__main__":
    try:
        registration_phase()
        lottery_draw()
    except KeyboardInterrupt:
        save_progress()
        log_event("Program interrupted. Progress saved.")
        print("\n🚨 Program interrupted. Registration data saved.")
