import random
import threading
import time
from screeninfo import get_monitors
import tkinter as tk

from PIL import Image, ImageTk
from src.consts import *
from src import config


popup_timer_thread = None  # the thread that runs the timer in the popup


# scale an image to cover the whole screen
def scale_image(img, width, height):
	img_ratio = img.width / img.height
	screen_ratio = width / height
	if img_ratio > screen_ratio:
		new_height = height
		new_width = int(new_height * img_ratio)
	else:
		new_width = width
		new_height = int(new_width / img_ratio)
	img = img.resize((new_width, new_height))
	return img


def add_main_window(monitor):
	config.root = tk.Tk()
	config.root.title("water time")
	config.root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

	# onclick for the close button. after the timer's up
	def close_window():
		config.root.destroy()

	# make fullscreen and always on top
	config.root.attributes('-fullscreen', True)
	config.root.wm_attributes('-topmost', True)

	# block any shortcuts that will switch away from the window
	# config.root.bind("<Alt_L>", lambda e: "break")
	# config.root.bind("<Tab>", lambda e: "break")
	# config.root.bind("<Escape>", lambda e: "break")
	# config.root.protocol("WM_DELETE_WINDOW", lambda: None)  # don't allow closing with alt f4 or any other way

	####### V now add the actual content... V #######

	canvas = tk.Canvas(config.root, highlightthickness=0)
	canvas.place(relwidth=1, relheight=1)

	def grid(row):
		return (monitor.width // 2, row * monitor.height // 10)

	# bg image
	bg_img = Image.open("./images/waterbg2.jpg")
	bg_img = scale_image(bg_img, monitor.width, monitor.height)  # scale the image to cover the entire screen...
	bg_img = ImageTk.PhotoImage(bg_img)
	canvas.bg_img_gc = bg_img  # keep a reference so it doesn't get garbage collected
	canvas.create_image((0, 0), image=bg_img, anchor="nw")

	# title text
	canvas.create_text(grid(1), text=random.choice(TITLES), fill=TEXT, font=("Arial", 52))

	# subtitle text
	canvas.create_text(grid(2), text=random.choice(SUBTITLES), fill=TEXT, font=("Arial", 26))

	# cat image
	file = "./images/cats/" + str(random.randint(1, NUM_CAT_IMAGES)) + ".png"  # pick a random image
	cat_img = Image.open(file)
	cat_img = cat_img.resize((int(cat_img.size[0] * 500 / cat_img.size[1]), 500))  # force height
	cat_img = ImageTk.PhotoImage(cat_img)
	canvas.cat_img_gc = cat_img  # keep a reference so it doesn't get garbage collected
	canvas.create_image(grid(3), image=cat_img, anchor="n")
	
	# button to close the thing. it starts out disabled
	close_button = tk.Button(config.root, text="", font=("Arial", 24), width=10, height=1, bg=PRIMARY_DARK, fg=PRIMARY_TEXT_DARK, state="disabled", bd=0, relief="flat", command=close_window)
	button_pos = grid(9)
	close_button.place(x=button_pos[0], y=button_pos[1], anchor="n")

	def enable_button():
		# change color to blue
		close_button.config(bg=PRIMARY, fg=PRIMARY_TEXT, activebackground=PRIMARY_DARK, activeforeground=PRIMARY_TEXT_DARK)
		# enable
		close_button.config(state="normal")
		# change color on hover
		close_button.bind("<Enter>", lambda e: close_button.config(bg=PRIMARY_DARK))
		close_button.bind("<Leave>", lambda e: close_button.config(bg=PRIMARY))

	# add timer that blocks you from pressing the button
	def timer():
		try:
			timer_duration = config.button_timer
			while timer_duration > 0 and not config.stop_event.is_set():
				config.root.after(0, lambda: close_button.config(text=str(timer_duration)  + " seconds"))
				time.sleep(1)
				timer_duration -= 1
			if not config.stop_event.is_set():
				config.root.after(0, lambda: close_button.config(text="i sipped"))
				config.root.after(0, enable_button)
		except RuntimeError:
			print("window closed")
	
	global popup_timer_thread
	popup_timer_thread = threading.Thread(target=timer, daemon=True)
	popup_timer_thread.start()


def add_secondary_window(monitor):
	window = tk.Toplevel(config.root)
	window.title("water time")
	# put this window on the correct monitor at these virtual coordinates
	window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

	# make fullscreen and always on top
	window.wm_attributes('-topmost', True)
	# window.attributes('-fullscreen', True)  # this won't work bc it'll move to the main monitor...
	window.overrideredirect(True)  # fake fullscreen by removing decoration etc

	# bg image
	file = "./images/bg/" + str(random.randint(1, NUM_BG_IMAGES)) + ".jpg"  # pick a random image
	img = Image.open(file)
	img = scale_image(img, monitor.width, monitor.height)  # scale the image to cover the entire screen...
	image = ImageTk.PhotoImage(img)
	image_label = tk.Label(window, image=image, bg=BG)
	image_label.place(relwidth=1, relheight=1)  # make it fill the window
	image_label.image = image  # keep a reference so it doesn't get garbage collected
	

def popup():
	monitors = get_monitors()

	# first, find the first primary monitor and create the main window
	primary_monitor = [m for m in monitors if m.is_primary][0]
	add_main_window(primary_monitor)
	
	monitors.remove(primary_monitor)  # remove the primary monitor from the monitors list...
	
	# then add secondary windows for all other monitors
	for monitor in monitors:
		add_secondary_window(monitor)

	config.root.mainloop()
