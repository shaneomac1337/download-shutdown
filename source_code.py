import psutil
import time
import os
import tkinter as tk
from tkinter import ttk
from threading import Thread

def get_network_bytes(interface):
    net_io = psutil.net_io_counters(pernic=True)
    return net_io[interface].bytes_recv

def monitor_network(interface, idle_time=20, shutdown=False, threshold=None):
    old_recv = get_network_bytes(interface)
    while not stop_monitoring_flag.get():
        time.sleep(1)
        new_recv = get_network_bytes(interface)
        download_speed = (new_recv - old_recv) / 1024 / 1024  # Convert to MB/s
        speed_label.config(text=f"Rychlost stahování: {download_speed:.2f} MB/s")
        if threshold is not None and download_speed < threshold / 1024:  # Convert threshold to MB/s
            idle_time -= 1
            status_label.config(text=f"Není zaznamenáno stahování, PC se vypne za {idle_time} sekund")
            if idle_time == 0:
                if shutdown:
                    status_label.config(text="Nezaznamenal jsem žádný traffic nad vybranou odchilkou, PC bude vypnuto.")
                    os.system("shutdown /s /t 60")
                break
        else:
            idle_time = 20  # Reset idle time if download speed is above threshold
            status_label.config(text="Stahování probíhá")
        root.update_idletasks()  # Update the GUI
        old_recv = new_recv

def start_monitoring():
    global speed_label
    interface = combo.get()
    threshold = None
    if use_threshold_var.get():
        threshold = int(threshold_entry.get())
        if threshold < 100:  # Prevent threshold from being set below 100
            threshold = 100
    stop_monitoring_flag.set(False)
    speed_label = ttk.Label(frame, text="Rychlost stahování: 0 MB/s")
    speed_label.grid(column=0, row=5, columnspan=2)  # Add the speed label to the grid
    Thread(target=monitor_network, args=(interface, 20, True, threshold)).start()

def stop_monitoring():
    stop_monitoring_flag.set(True)
    speed_label.destroy()  # Destroy the speed label
    status_label.config(text="")
    monitoring_button.config(text="Monitorovat", command=toggle_monitoring)
    root.after(1000, lambda: status_label.config(text=""))  # Reset status label after 1 second

def toggle_monitoring():
    if stop_monitoring_flag.get():
        start_monitoring()
        monitoring_button.config(text="Zastavit monitoring", command=stop_monitoring)
    else:
        stop_monitoring()
        monitoring_button.config(text="Monitorovat", command=start_monitoring)

root = tk.Tk()
root.geometry('319x171')  # Set window size to 319x171
root.title("Shutdown tool by Shane")
#root.resizable(False, False)  # Disable resizing the window

frame = ttk.Frame(root, padding="10")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

label = ttk.Label(frame, text="Vyberte síťový adaptér:")
label.grid(column=0, row=0, sticky=tk.W)

combo = ttk.Combobox(frame, values=list(psutil.net_io_counters(pernic=True).keys()))
combo.grid(column=1, row=0, sticky=(tk.W, tk.E))
combo.set('Ethernet')  # Set default value

use_threshold_var = tk.IntVar(value=1)
use_threshold_checkbutton = ttk.Checkbutton(frame, text="Minimální rychlost k detekci stahování", variable=use_threshold_var, state='disabled')
use_threshold_checkbutton.grid(column=0, row=1, sticky=tk.W)

threshold_label = ttk.Label(frame, text="Nastavení rychlost (kbps):")
threshold_label.grid(column=0, row=2, sticky=tk.W)

threshold_entry = ttk.Entry(frame)
threshold_entry.grid(column=1, row=2, sticky=(tk.W, tk.E))
threshold_entry.insert(0, "200")  # Set default value

empty_label = ttk.Label(frame, text="")
empty_label.grid(column=0, row=4, columnspan=2)

monitoring_button = ttk.Button(frame, text="Monitorovat", command=toggle_monitoring)
monitoring_button.grid(column=0, row=9, columnspan=5)

status_label = ttk.Label(frame, text="")
status_label.grid(column=0, row=6, columnspan=2)

stop_monitoring_flag = tk.BooleanVar(value=True)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)

root.mainloop()