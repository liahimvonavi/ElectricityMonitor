import csv
import time
from datetime import datetime
from relay_control import Relay_Manager

plan = {}

manager = Relay_Manager()

def log_operation(action, state, hour):
    with open("relay_log.csv", "a", newline="") as logfile:
        writer = csv.writer(logfile)
        writer.writerow([datetime.now().isoformat(), action, state, hour])

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
            break
        else:
            log_operation("Inverters were already on nothing to do", "on", current_hour)
            break
    time.sleep(60)
