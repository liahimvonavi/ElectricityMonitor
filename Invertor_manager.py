import csv
import time
from datetime import datetime, timedelta
from relay_control import Relay_Manager
from send_mail import notify
import traceback

plan = {}

manager = Relay_Manager()

def sleep_until_next_hour():
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    sleep_duration = (next_hour - now).total_seconds()
    time.sleep(sleep_duration)

def log_operation(action, state, hour):
    with open("relay_log.csv", "a", newline="") as logfile:
        writer = csv.writer(logfile)
        writer.writerow([datetime.now().isoformat(), action, state, hour])

def cleanup_old_logs(days, log_file):
    try:
        with open(log_file, newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

        cutoff = datetime.now() - timedelta(days=days)
        cleaned_rows = []

        for row in rows:
            try:
                log_time = datetime.fromisoformat(row[0])
                if log_time >= cutoff:
                    cleaned_rows.append(row)
            except (ValueError, IndexError):
                continue

        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(cleaned_rows)

    except FileNotFoundError:
        pass
try:
    last_state = 'on'
    with open("relay_plan.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            plan[int(row['hour'])] = row['state']

    while True:
        current_hour = datetime.now().hour

        if plan.get(current_hour) == "on" and last_state != "on":
            log_operation("Inverter command", "on", current_hour)
            manager.relay_mode(mode="on")
            last_state = "on"
        elif plan.get(current_hour) == "off" and last_state != "off":
            log_operation("Inverter command", "off", current_hour)
            manager.relay_mode(mode="off")
            last_state = "off"
        if current_hour >= 20:
            if last_state != "on":
                log_operation("Inverters forced on", "on", current_hour)
                last_state="on"
                manager.relay_mode(mode="on")
                cleanup_old_logs(days=60, log_file="inverter_operation_log.csv")
                cleanup_old_logs(days=60, log_file="relay_log.csv")
                break
            else:
                log_operation("Inverters were already on nothing to do", "on", current_hour)
                cleanup_old_logs(days=60, log_file="inverter_operation_log.csv")
                cleanup_old_logs(days=60, log_file="relay_log.csv")
                break
        sleep_until_next_hour()
except Exception as e:
    error_msg = traceback.format_exc()
    with open("fatal_errors.log", "a") as f:
        f.write(f"{datetime.now().isoformat()} {error_msg}\n")
    notify(error_msg)
    # notify(error_msg)