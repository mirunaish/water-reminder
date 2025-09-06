import time
from pystray import Icon as _Icon, Menu, MenuItem as item
from PIL import Image
import threading
from src import config


# create a custom icon class to override the _on_notify method
# so i can capture clicks...
class Icon(_Icon):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def _on_notify(self, wparam, lparam):
		# 0x200 = WM_MOUSEHOVER
		# 0x201 = WM_LBUTTONDOWN
		# 0x202 = WM_LBUTTONUP
		# 0x203 = WM_LBUTTONDBLCLK
		# 0x204 = WM_RBUTTONDOWN
		# 0x205 = WM_RBUTTONUP
		# 0x206 = WM_RBUTTONDBLCLK

		# if i right clicked and opened the menu, update the menu with the correct remaining time
		if lparam == 0x201 or lparam == 0x204:
			self.update_menu()

		super()._on_notify(wparam, lparam)


def get_time_until_popup():
	now = time.time()
	elapsed_time = now - config.waiting_start_time
	time_left = config.waiting_time + config.skip_time - elapsed_time

	hours = int(time_left // 3600)
	minutes = int((time_left % 3600) // 60)
	seconds = int(time_left % 60)
	
	if time_left <= 0:
		return "showing popup now"
	
	if hours > 0:
		return f"{hours}h {minutes}m {seconds}s"
	elif minutes > 0:
		return f"{minutes}m {seconds}s"
	else:
		return f"{seconds}s"

def load_icon():
	return Image.open("water.ico")

# don't show the popup for a duration
def pause(duration):
	config.skip_time += duration

def set_popup_timer(timer):
	config.popup_timer = timer

# close everything and quit
def on_quit(icon, _):
    config.stop_event.set()
    icon.stop()
    try:
        config.root.destroy()
        config.root.quit()
    except Exception as e:
        print("couldn't stop root")


def menu_items():
	time_remaining_item = item("time until next popup: " + get_time_until_popup(), lambda: None)
	delay_items = [item("show every 15 minutes", lambda: set_popup_timer(15*60)), item("show every 30 minutes", lambda: set_popup_timer(30*60)), item("show every hour", lambda: set_popup_timer(60*60))]
	pause_items = [item("pause for 1h", lambda: pause(3600)), item("pause for 2h", lambda: pause(3600*2)), item("pause for 3h", lambda: pause(3600*3))]
	return (time_remaining_item, *delay_items, *pause_items, item("quit", on_quit))

def tray_icon():
	config.icon = Icon("water", load_icon(), "water time", menu=Menu(menu_items))
	config.icon.run_detached()


# start the tray icon thread
def start_tray_thread():
	icon_thread = threading.Thread(target=tray_icon, daemon=True)
	icon_thread.start()
