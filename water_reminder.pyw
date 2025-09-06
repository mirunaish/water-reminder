import tkinter as tk
import random
import threading
import time
from pystray import Icon, Menu, MenuItem as item
from PIL import Image, ImageTk


titles = ["it's water time", "take a sip of water", "hydration break", "hydration station", "mandatory water break",
          "thirst check"]
subtitles = ["you are dehydrated....", "water is good for you", "you can't leave until you take a sip", 
             "i am here to remind you to hydrate regularly", "cold delicious water",
             "you gotta wait anyway, might as well take a sip", "water is the source of all life. drink some",
             "pay attention to what your body is telling you. you're thirsty", 
             "you're stuck here until you drink some water.", "stretch a bit too while you're at it.",
             "whatever you were doing can wait. drink some water", "water will give you energy"]

bg = "lightblue"
text = "blue"
fineprint = "darkblue"
primary = "blue"
primary_dark = "darkblue"
primary_text = "white"
primary_text_dark = "lightblue"

button_timer = 10  # 10 seconds before you can close the popup
popup_timer = 30*60  # 30 minutes

def load_icon():
    return Image.open("water.ico")

stop_event = threading.Event()  # tell everyone to stop immediately
skips = 0  # skip this many popups


def popup():
    global root
    root = tk.Tk()
    root.title("water time")

    # configure grid so everything is laid out nicely in the window
    root.grid_columnconfigure(0, weight=1)  # fill entire window
    root.grid_rowconfigure(0, weight=2)  # title
    root.grid_rowconfigure(1, weight=1)  # subtitle
    root.grid_rowconfigure(2, weight=2)  # image
    root.grid_rowconfigure(3, weight=1)  # timer
    root.grid_rowconfigure(4, weight=2)  # button

    def close_window():
        root.destroy()

    # make fullscreen and always on top
    root.attributes('-fullscreen', True)
    root.wm_attributes('-topmost', True)

    # block any shortcuts that will switch away from the window
    # root.bind("<Alt_L>", lambda e: "break")
    # root.bind("<Tab>", lambda e: "break")
    # root.bind("<Escape>", lambda e: "break")
    # root.protocol("WM_DELETE_WINDOW", lambda: None)  # don't allow closing with alt f4 or any other way

    ####### V now add the actual content... V #######

    # bg color
    root.configure(bg=bg)

    # title text
    title = tk.Label(root, text=random.choice(titles), font=("Arial", 70), fg=text, bg=bg)
    root.after(100, lambda: title.config(wraplength=root.winfo_width() - 100))
    title.grid(row=0, column=0, sticky="nsew")

    # subtitle text
    subtitle = tk.Label(root, text=random.choice(subtitles), font=("Arial", 40), fg=text, bg=bg)
    root.after(100, lambda: subtitle.config(wraplength=root.winfo_width() - 100))
    subtitle.grid(row=1, column=0, sticky="nsew")

    # image
    file = "./images/" + str(random.randint(1, 5)) + ".png"  # pick a random image
    img = Image.open(file)
    img = img.resize((int(img.size[0] * 300 / img.size[1]), 300))
    image = ImageTk.PhotoImage(img)
    image_label = tk.Label(root, image=image, bg=bg)
    image_label.grid(row=2, column=0, sticky="nsew")
    image_label.image = image

    # timer text
    timer_label = tk.Label(root, text="", font=("Arial", 16), fg=fineprint, bg=bg)
    timer_label.grid(row=3, column=0, sticky="sew")

    # button to close the thing. it starts out disabled
    close_button = tk.Button(root, text="i sipped", font=("Arial", 30), width=10, height=1, bg=primary_dark, fg=primary_text_dark, state="disabled", bd=0, relief="flat", command=close_window)
    close_button.grid(row=4, column=0, sticky="")

    def enable_button():
        # change color to blue
        close_button.config(bg=primary, fg=primary_text, activebackground=primary_dark, activeforeground=primary_text_dark)
        # enable
        close_button.config(state="normal")
        # change color on hover
        close_button.bind("<Enter>", lambda e: close_button.config(bg=primary_dark))
        close_button.bind("<Leave>", lambda e: close_button.config(bg=primary))

    # add timer that blocks you from pressing the button
    def timer():
        try:
            timer_duration = button_timer
            while timer_duration > 0 and not stop_event.is_set():
                root.after(0, lambda: timer_label.config(text="can close in " + str(timer_duration)  + " seconds"))
                time.sleep(1)
                timer_duration -= 1
            if not stop_event.is_set():
                root.after(0, lambda: timer_label.config(text=""))
                root.after(0, enable_button)
        except RuntimeError:
            print("window closed")

    global timer_thread
    timer_thread = threading.Thread(target=timer, daemon=True)
    timer_thread.start()

    root.mainloop()


# V tray functions: V

# stop everything
def on_quit(icon, _):
    stop_event.set()
    icon.stop()

    try:
        root.destroy()
        root.quit()
    except Exception as e:
        print("couldn't stop root")


# don't show the popup for a duration
def pause(duration):
    global skips
    skips += duration / popup_timer

def set_popup_timer(timer):
    global popup_timer
    popup_timer = timer


# start the tray icon thread
def tray_icon():
    delay_items = [item("show every 15 minutes", lambda: set_popup_timer(15*60)), item("show every 30 minutes", lambda: set_popup_timer(30*60)), item("show every hour", lambda: set_popup_timer(60*60))]
    pause_items = [item("pause for 1h", lambda: pause(3600)), item("pause for 2h", lambda: pause(3600*2)), item("pause for 3h", lambda: pause(3600*3))]
    icon = Icon("water", load_icon(), "water time", menu=Menu(*delay_items, *pause_items, item("quit", on_quit)))
    icon.run()

icon_thread = threading.Thread(target=tray_icon, daemon=True)
icon_thread.start()


# main loop: wait and then show popup
while not stop_event.is_set():
    if stop_event.wait(popup_timer):
        # if the stop event was set while waiting, stop main loop
        break

    # if i asked to pause popups, skip this popup... just wait again
    if skips > 0:
        skips -= 1
        continue

    popup()
