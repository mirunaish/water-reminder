import random
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
from src.consts import *
from src import config


popup_timer_thread = None  # the thread that runs the timer in the popup


def popup():
	config.root = tk.Tk()
	config.root.title("water time")

	# configure grid so everything is laid out nicely in the window
	config.root.grid_columnconfigure(0, weight=1)  # fill entire window
	config.root.grid_rowconfigure(0, weight=2)  # title
	config.root.grid_rowconfigure(1, weight=1)  # subtitle
	config.root.grid_rowconfigure(2, weight=2)  # image
	config.root.grid_rowconfigure(3, weight=1)  # timer
	config.root.grid_rowconfigure(4, weight=2)  # button

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

	# bg color
	config.root.configure(bg=BG)

	# title text
	title = tk.Label(config.root, text=random.choice(TITLES), font=("Arial", 70), fg=TEXT, bg=BG)
	config.root.after(100, lambda: title.config(wraplength=config.root.winfo_width() - 100))
	title.grid(row=0, column=0, sticky="nsew")

	# subtitle text
	subtitle = tk.Label(config.root, text=random.choice(SUBTITLES), font=("Arial", 40), fg=TEXT, bg=BG)
	config.root.after(100, lambda: subtitle.config(wraplength=config.root.winfo_width() - 100))
	subtitle.grid(row=1, column=0, sticky="nsew")

	# image
	file = "./images/cats/" + str(random.randint(1, NUM_CAT_IMAGES)) + ".png"  # pick a random image
	img = Image.open(file)
	img = img.resize((int(img.size[0] * 300 / img.size[1]), 300))  # force height to 300
	image = ImageTk.PhotoImage(img)
	image_label = tk.Label(config.root, image=image, bg=BG)
	image_label.grid(row=2, column=0, sticky="nsew")
	image_label.image = image

	# timer text
	timer_label = tk.Label(config.root, text="", font=("Arial", 16), fg=FINEPRINT, bg=BG)
	timer_label.grid(row=3, column=0, sticky="sew")

	# button to close the thing. it starts out disabled
	close_button = tk.Button(config.root, text="i sipped", font=("Arial", 30), width=10, height=1, bg=PRIMARY_DARK, fg=PRIMARY_TEXT_DARK, state="disabled", bd=0, relief="flat", command=close_window)
	close_button.grid(row=4, column=0, sticky="")

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
				config.root.after(0, lambda: timer_label.config(text="can close in " + str(timer_duration)  + " seconds"))
				time.sleep(1)
				timer_duration -= 1
			if not config.stop_event.is_set():
				config.root.after(0, lambda: timer_label.config(text=""))
				config.root.after(0, enable_button)
		except RuntimeError:
			print("window closed")

	global popup_timer_thread
	popup_timer_thread = threading.Thread(target=timer, daemon=True)
	popup_timer_thread.start()

	config.root.mainloop()