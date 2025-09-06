import threading

button_timer = 10  # 10 seconds before you can close the popup
popup_timer = 30*60  # 30 minutes. in seconds
skip_time = 0  # skip this many seconds

waiting_time = 0  # the time i will wait. will set to popup timer at the time of starting waiting
# ^ so i can still get an accurate idea of how long i have to wait even if i change popup_timer
waiting_start_time = 0  # the time i started waiting for next popup

root = None  # the popup window
icon = None  # the tray icon

stop_event = threading.Event()  # tell everyone to stop immediately