#!/bin/env python3
import systemd_watchdog
import time

wd = systemd_watchdog.watchdog()

# Report a status message
wd.status("Starting my service...")
time.sleep(1)

# Report that the program init is complete - "systemctl start" won't return until ready() called if Type=notify
wd.ready()
wd.notify()

timeout_half_sec = int(float(wd.timeout) / 2e6)  # Convert us->s and half that
wd.status("Waiting {} seconds (1/2)".format(timeout_half_sec))
time.sleep(timeout_half_sec)
wd.notify()

wd.status("Waiting {} seconds (2/2)".format(timeout_half_sec))
time.sleep(timeout_half_sec)
wd.notify()

count = 0
while not wd.notify_due:
    count += 1
    wd.status("Waiting for notify_due flag: iteration {}".format(count))
    time.sleep(0.1)  # BUSY LOOPS ARE BAD

# In theory, the ONLY call you would ever need is ping(); it handles all the bookkeeping for you.
# It is designed to sit in your event loop and you normally won't care about the return value.
# systemctl --user status systemd-watchdog-example.service will show the text
sends = []
count = 0
max_count = 300
wd.status("In ping() loop for {}s".format(max_count*0.1))
while count < max_count:
    count += 1
    sends.append(wd.ping())
    time.sleep(0.1)
    if (count % 10) == 0:
        wd.status("In ping() loop for {}s - {}s elapsed".format(max_count*0.1, count*0.1))
wd.status("ping() sent {} messages out of {} calls".format(sum(sends), max_count))
time.sleep(5)

# Report an error to the service manager
# wd.notify_error("Blowing up on purpose!")
# The service manager will probably kill the program here

wd.status("Simulating hang")
wd.notify()
time.sleep(120)
