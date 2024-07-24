import tkinter as tk
from tkinter import messagebox
from tkinter import Canvas
from PIL import Image, ImageTk
import os
import requests
import json
import time
import pygame
from tkinter import ttk
import turtle
from background_animation import draw_background  # Import the function
import webbrowser
import pyperclip  # Add this import for copying to clipboard

# Initialize pygame
pygame.init()

# Load the music file
music_file = "background_music.mp3"  # Change this to your music file path
pygame.mixer.music.load(music_file)

# Start playing the music (set -1 for loop indefinitely)
pygame.mixer.music.play(-1)

# Get the directory path of the script file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the project directory as the parent directory of the script directory
project_dir = os.path.abspath(os.path.join(script_dir, ".."))

# Define other paths relative to the project directory
get_map_dir = os.path.join(project_dir, "Step1–GetCornerPoints")
get_countries_dir = os.path.join(project_dir, "Step2_Create_Country_Polygons")
country_name_dir = os.path.join(project_dir, "Project1_CountryName")

# Explanations for each button
explanations = {
    "get_map_button": "نقشه را تنظیم کنید",
    "get_countries_button": "کشور های جدید را اضافه کنید",
    "country_name_button": "کشور ها",
    "explanations_button": "اطلاعات"
}

# Store the original text of each button
original_texts = {
    "get_map_button": "Set The Map",
    "get_countries_button": "Get New Countries",
    "country_name_button": "Country Name",
    "explanations_button": "Contact Me"
}
# Define a variable to store the position of music when muted
muted_position = 0

def toggle_sound():
    global muted_position
    if pygame.mixer.music.get_busy():
        # Store the current position of the music
        muted_position = pygame.mixer.music.get_pos()
        # Stop the music
        pygame.mixer.music.stop()
        sound_button.config(image=sound_off_img)
    else:
        # Resume playing from the stored position
        pygame.mixer.music.play(-1, start=muted_position)
        sound_button.config(image=sound_on_img)

# Function to update button text with explanations
def update_button_text(event, button_name):
    if button_name in explanations:
        # Store the original text of the button
        original_texts[button_name] = event.widget.cget("text")
        # Update the button text with the explanation
        event.widget.config(text=explanations[button_name])

# Function to restore button text to original
def restore_button_text(event, button_name):
    if button_name in original_texts:
        # Restore the original text of the button
        event.widget.config(text=original_texts[button_name])

def run_get_map():
    os.chdir(get_map_dir)
    os.system("python get_map.py")
    os.chdir(project_dir)

def run_get_countries():
    os.chdir(get_countries_dir)
    os.system("python get_countries.py")
    os.chdir(project_dir)

def run_country_name():
    os.chdir(country_name_dir)
    os.system("python country_name.py")
    os.chdir(project_dir)

# Function to show explanations with links
def show_explanations():
    def open_telegram():
        webbrowser.open("https://telegram.me/mahdi1380sha")

    def open_whatsapp():
        webbrowser.open("https://wa.me/989902864827")

    def copy_email():
        email = "mahdi1380shafizadeh@outlook.com"
        pyperclip.copy(email)
        messagebox.showinfo("Email Copied", f"Email copied to clipboard: {email}")

    message = "If you have any questions, you can contact me in one of the following ways:\n\n"

    custom_message_box = tk.Toplevel(root)
    custom_message_box.title("Contact Me")
    custom_message_box.configure(bg="#AAAAAA")

    label = tk.Label(custom_message_box, text=message, wraplength=750, font=("Arial", 16), bg="#AAAAAA", fg="#2A623D")
    label.pack(pady=10)

    # Create a custom style
    style = ttk.Style()
    style.configure("Custom.TButton", font=("Arial", 16), background="#FFD700", foreground="#2A623D")  # Default style

    # Button for Telegram
    telegram_button = ttk.Button(custom_message_box, text="Telegram", command=open_telegram, style="Custom.TButton")
    telegram_button.pack(pady=5)

    # Button for WhatsApp
    whatsapp_button = ttk.Button(custom_message_box, text="WhatsApp", command=open_whatsapp, style="Custom.TButton")
    whatsapp_button.pack(pady=5)

    # Button for copying email
    email_button = ttk.Button(custom_message_box, text="Email", command=copy_email, style="Custom.TButton")
    email_button.pack(pady=5)

# Define a variable to store the position of music when muted
muted_position = 0

def toggle_sound():
    global muted_position
    if pygame.mixer.music.get_busy():
        # Store the current position of the music
        muted_position = pygame.mixer.music.get_pos()
        # Stop the music
        pygame.mixer.music.stop()
        sound_button.config(image=sound_off_img)
    else:
        # Resume playing from the stored position
        pygame.mixer.music.play(-1, start=muted_position)
        sound_button.config(image=sound_on_img)

def exit_program():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        # Stop the music
        pygame.mixer.music.stop()
        root.destroy()

def resize_logo(image_path, target_size=(1920, 1080)):
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Resize the image to the target size
            resized_img = img.resize(target_size, Image.LANCZOS)

        return resized_img
    except Exception as e:
        print("Failed to resize the logo image.")
        print("Error:", e)
        return None

def sample_color(image_path):
    try:
        with Image.open(image_path) as img:
            # Sample the color from the single pixel at the center of the image
            color = img.getpixel((img.width // 2, img.height // 2))
            # Convert RGB color to hexadecimal format
            hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
            return hex_color
    except Exception as e:
        print("Failed to sample color from image.")
        print("Error:", e)
        return None

def update_location():
    try:
        # Fetch location information using IP geolocation service
        response = requests.get("http://ipinfo.io/json")
        data = response.json()

        # Extract city from the location data
        city = data.get("city", "Unknown")  # Default to "Unknown" if city information is not available

        # Update the city label with the retrieved city
        city_label.config(text=city)
    except Exception as e:
        print("Failed to fetch location information.")
        print("Error:", e)
        # Set "Unknown" as default city if unable to fetch location information
        city_label.config(text="Tehran")

def update_clock():
    current_time = time.strftime("%H:%M:%S")
    time_label.config(text=current_time)
    root.after(1000, update_clock)  # Update every second

def update_date():
    current_date = time.strftime("%Y-%m-%d")
    date_label.config(text=current_date)

def on_enter(event):
    sound_button.config(image=sound_on_img_hover)

def on_leave(event):
    if pygame.mixer.music.get_busy():
        sound_button.config(image=sound_on_img)
    else:
        sound_button.config(image=sound_off_img)

# Create the main window
root = tk.Tk()
root.title("Interactive Map Tool")

# Set window size to full screen
root.attributes("-fullscreen", True)

# Draw the background animation
background_canvas = draw_background(root)

# Sample color from the logo image
label_bg_color = "#5D5D5D"  # Use your sampled color here or set a default color

# Welcome label with background color
welcome_label = tk.Label(root, text="Welcome! To get started, please choose one of the following options:", font=("Arial", 40), bg=label_bg_color, fg="#1A472A")
welcome_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

# Create a frame for the buttons
button_frame = tk.Frame(root, bg=label_bg_color)
button_frame.place(relx=0.02, rely=0.9, anchor=tk.SW)

# Style for the buttons
style = ttk.Style()
style.configure("TButton", borderwidth=5, relief="ridge", bordercolor=label_bg_color, font=("Arial", 20), background=label_bg_color, fg="#1A472A")

# Buttons
get_map_button = ttk.Button(button_frame, text="Set The Map", command=run_get_map, width=20, padding=40, style="Custom.TButton")
get_map_button.grid(row=0, column=0, pady=10, sticky="w")
get_map_button.bind("<Enter>", lambda event: update_button_text(event, "get_map_button"))
get_map_button.bind("<Leave>", lambda event: restore_button_text(event, "get_map_button"))

get_countries_button = ttk.Button(button_frame, text="Get New Countries", command=run_get_countries, width=20, padding=40, style="Custom.TButton")
get_countries_button.grid(row=1, column=0, pady=10, sticky="w")
get_countries_button.bind("<Enter>", lambda event: update_button_text(event, "get_countries_button"))
get_countries_button.bind("<Leave>", lambda event: restore_button_text(event, "get_countries_button"))

country_name_button = ttk.Button(button_frame, text="Country Name", command=run_country_name, width=20, padding=40, style="Custom.TButton")
country_name_button.grid(row=2, column=0, pady=10, sticky="w")
country_name_button.bind("<Enter>", lambda event: update_button_text(event, "country_name_button"))
country_name_button.bind("<Leave>", lambda event: restore_button_text(event, "country_name_button"))

explanations_button = ttk.Button(button_frame, text="Contact Me", command=show_explanations, width=20, padding=40, style="Custom.TButton")
explanations_button.grid(row=3, column=0, pady=10, sticky="w")
explanations_button.bind("<Enter>", lambda event: update_button_text(event, "explanations_button"))
explanations_button.bind("<Leave>", lambda event: restore_button_text(event, "explanations_button"))

style = ttk.Style()
style.configure("Custom.TButton", borderwidth=5, relief="ridge", bordercolor="#AAAAAA", font=("Arial", 20), background="#5D5D5D", foreground="#2A623D")

# Sound button
sound_on_img = ImageTk.PhotoImage(Image.open("sound_on.png"))
sound_off_img = ImageTk.PhotoImage(Image.open("sound_off.png"))
sound_on_img_hover = ImageTk.PhotoImage(Image.open("sound_on_hover.png"))
sound_button = tk.Button(root, image=sound_on_img, bd=0, bg=label_bg_color, highlightbackground=label_bg_color, command=toggle_sound)
sound_button.place(x=10, y=root.winfo_screenheight() - 50)
sound_button.bind("<Enter>", on_enter)
sound_button.bind("<Leave>", on_leave)


# Time label
time_label = tk.Label(root, text="", font=("Arial", 14), bg=label_bg_color)
time_label.place(relx=0.98, rely=0.9, anchor=tk.SE)

# Date label
date_label = tk.Label(root, text="", font=("Arial", 14), bg=label_bg_color)
date_label.place(relx=0.98, rely=0.94, anchor=tk.SE)

# City label
city_label = tk.Label(root, text="", font=("Arial", 14), bg=label_bg_color)
city_label.place(relx=0.98, rely=0.98, anchor=tk.SE)

# Update location information
update_location()

# Update clock
update_clock()

# Update date
update_date()

# Bind the Escape key to exit the program
root.bind("<Escape>", lambda event: exit_program())
def toggle_music_with_key(event):
    if event.keysym == "m" or event.keysym == "M":
        toggle_sound()

# Bind the "M" key to toggle the music
root.bind("<KeyPress>", toggle_music_with_key)

# Run the main event loop
root.mainloop()
