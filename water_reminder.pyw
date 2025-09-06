import time
from src.consts import *
from src import config
from src.tray import start_tray_thread
from src.popup import popup


start_tray_thread()

# main loop: wait and then show popup
while not config.stop_event.is_set():
    config.waiting_start_time = time.time()

    if config.skip_time > 0:
        # if i added skip time, wait that amount
        config.waiting_time = config.skip_time
        config.skip_time = 0  # reset skip time
    else:
        # otherwise wait the default timer
        config.waiting_time = config.popup_timer

    if config.stop_event.wait(config.waiting_time):
        # if the stop event was set while waiting, i probably clicked the quit button in tray
        # so break out of the loop and end the program
        break

    if config.skip_time > 0:
        # if i added skip time while waiting, skip this popup and wait again for skip_time
        continue

    popup()
