import tkinter as tk
from tkinter import filedialog
import cv2
import subprocess
import time
import os
import threading


class LegendOfMushroomBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Legend of Mushroom")

        self.running = False
        self.app_state = AppState()
        self.program_dir = os.path.dirname(os.path.realpath(__file__))
        self.file_path = os.path.join(self.program_dir, "configs.txt")

        # Constants
        self.ENTER_IMAGE_PATH = 'images/enter.png'
        self.ENTER_2_IMAGE_PATH = 'images/enter_2.png'
        self.DUNGEON_IMAGE_PATH = 'images/dungeon.png'
        self.SELL_IMAGE_PATH = 'images/sell.png'
        self.CANCEL_IMAGE_PATH = 'images/cancel.png'
        self.AUTO_IMAGE_PATH = 'images/auto.png'
        self.POPUP_IMAGE_PATH = 'images/popup.png'
        self.CHALLENGE_IMAGE_PATH = 'images/challenge.png'

        self.load_constants()

        # UI setup
        self.setup_ui()

        # Load configurations
        self.load_configs()

    def load_constants(self):
        self.enter_image = cv2.imread(self.ENTER_IMAGE_PATH)
        self.enter_2_image = cv2.imread(self.ENTER_2_IMAGE_PATH)
        self.dungeon_image = cv2.imread(self.DUNGEON_IMAGE_PATH)
        self.sell_image = cv2.imread(self.SELL_IMAGE_PATH)
        self.cancel_image = cv2.imread(self.CANCEL_IMAGE_PATH)
        self.auto_image = cv2.imread(self.AUTO_IMAGE_PATH)
        self.popup_image = cv2.imread(self.POPUP_IMAGE_PATH)
        self.challenge_image = cv2.imread(self.CHALLENGE_IMAGE_PATH)

    def setup_ui(self):
        self.root.geometry("400x500")  # Set initial window size

        # Emulator Script title
        tk.Label(self.root, text="Mushroom Legends Bot", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Frame to hold emulator path selection button and label
        select_path_frame = tk.Frame(self.root)
        select_path_frame.pack(pady=5)

        # Select emulator path button
        self.select_path_button = tk.Button(select_path_frame, text="Select Emulator Path", command=self.select_emulator_path, font=("Helvetica", 10))
        self.select_path_button.pack(side=tk.LEFT, padx=5)

        # Label to display selected path
        self.selected_emulator_label = tk.Label(select_path_frame, text="", font=("Helvetica", 10))
        self.selected_emulator_label.pack(side=tk.LEFT)

        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Roll Lamp button
        self.start_button = tk.Button(button_frame, text="Roll Lamp", command=self.start_script_thread, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Go Dungeon button
        self.start_dungeon_button = tk.Button(button_frame, text="Go Dungeon", command=self.start_dungeon_thread, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.start_dungeon_button.pack(side=tk.LEFT, padx=5)

        # Stop Script button
        self.stop_button = tk.Button(self.root, text="Stop Script", command=self.stop_script, state=tk.DISABLED, width=12, relief=tk.RAISED, bd=3, font=("Helvetica", 10))
        self.stop_button.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="Status: Not running", font=("Helvetica", 10))
        self.status_label.pack()

        # Log text
        self.log_text = tk.Text(self.root, font=("Helvetica", 10))
        self.log_text.pack()

    def load_configs(self):
        """Load configurations from file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    for line in f:
                        if line.startswith("path = "):
                            preloaded_path = line.strip().split('= "')[1].strip('"')
                            if preloaded_path:
                                self.app_state.set_programm_path(preloaded_path)
                                self.selected_emulator_label.config(text=preloaded_path)
                                self.log_message(f"Preloaded path: {preloaded_path}")
                        if line.startswith("emulator = "):
                            preloaded_path = line.strip().split('= "')[1].strip('"')
                            if preloaded_path:
                                self.app_state.set_emulator_name(preloaded_path)
            except IOError as e:
                self.log_message(f"Error reading path file: {e}")

    def save_config_to_file(self, config_key, config_value, filename="configs.txt"):
        """Save a configuration key-value pair to a file."""
        program_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(program_dir, filename)

        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith(f"{config_key} ="):
                            lines[lines.index(line)] = f"{config_key} = \"{str(config_value)}\"\n"
                            with open(file_path, "w") as f:
                                f.writelines(lines)
                            self.log_message(f"Configuration updated successfully in: {file_path}")
                            return

            with open(file_path, "a") as f:
                f.write(f"{config_key} = \"{str(config_value)}\"\n")
            self.log_message(f"Configuration added successfully to: {file_path}")
        except IOError as e:
            self.log_message(f"Error saving configuration: {e}")

    def select_emulator_path(self):
        """Select emulator path."""
        emulator_path = filedialog.askdirectory()
        if emulator_path:
            original_dir = os.getcwd()
            os.chdir(emulator_path)
            try:
                devices = subprocess.check_output(["adb", "devices"]).decode("utf-8")
                connected_devices = [line.split("\t")[0] for line in devices.splitlines()[1:]]
                if connected_devices:
                    self.log_message(str(connected_devices))
                    found = False
                    for connected_device in connected_devices:
                        if connected_device.startswith("emulator"):
                            self.app_state.set_emulator_name(connected_device)
                            self.save_config_to_file("emulator", connected_device)
                            self.selected_emulator_label.config(text=f"{emulator_path}")
                            self.app_state.set_programm_path(emulator_path)
                            self.save_config_to_file("path", emulator_path)
                            self.log_message("Successful connection 🚀")
                            found = True
                    if not found:
                        self.log_message("No devices connected")
                else:
                    self.log_message("No devices connected")
            except subprocess.CalledProcessError as e:
                self.log_message("Error checking ADB connection")
            finally:
                os.chdir(original_dir)

    def log_message(self, message):
        """Log messages to the UI."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def start_script_thread(self):
        """Start the script in a separate thread."""
        threading.Thread(target=self.start_script).start()

    def start_dungeon_thread(self):
        """Start the dungeon in a separate thread."""
        threading.Thread(target=self.start_dungeon).start()

    def start_script(self):
        """Start the script."""
        if not self.app_state.programm_path:
            self.log_message("Please select emulator path first.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.start_dungeon_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")

        # Run the script
        self.run_script()

    def start_dungeon(self):
        """Start the dungeon."""
        if not self.app_state.programm_path:
            self.log_message("Please select emulator path first.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.start_dungeon_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running")

        # Run the dungeon
        self.run_dungeon()

    def stop_script(self):
        """Stop the script."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.start_dungeon_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Not running")

    def connect_to_emulator(self):
        """Connect to the emulator."""
        self.log_message("Connecting to the emulator...")
        subprocess.run([os.path.join(self.app_state.programm_path, 'adb'), 'connect', self.app_state.emulator_name])
        self.log_message("Connection successful.")

    def click_position(self, x, y):
        """Click at a specific position."""
        self.log_message(f"Clicking at position ({x}, {y})")
        subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)])
        self.log_message("Click performed.")

    def take_screenshot(self):
        """Take a screenshot."""
        original_dir = os.getcwd()
        images_dir = os.path.join(original_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        screenshot_path = os.path.join(images_dir, "screenshot.png")

        subprocess.run(["adb", "-s", self.app_state.emulator_name, "shell", "screencap", "/sdcard/screenshot.png"])
        subprocess.run(["adb", "-s", self.app_state.emulator_name, "pull", "/sdcard/screenshot.png", screenshot_path])
        self.log_message("Screenshot taken.")
        return cv2.imread(screenshot_path)

    def find_subimage(self, screenshot, subimage):
        """Find a subimage on the screen."""
        result = cv2.matchTemplate(screenshot, subimage, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.8:
            self.log_message("Found subimage")
        return max_loc, max_val

    def check_for_another_subimage(self, screenshot, subimage):
        """Check if another subimage exists."""
        self.log_message("Checking if another subimage exists...")
        _, similarity = self.find_subimage(screenshot, subimage)
        self.log_message("Check complete.")
        return similarity > 0.8

    def perform_additional_clicks(self):
        """Perform additional clicks."""
        self.log_message("Performing additional clicks...")
        self.click_position(598, 916)
        time.sleep(0.2)
        self.click_position(608, 1328)
        self.log_message("Additional clicks performed.")

    def run_script(self):
        """Run the script."""
        os.chdir(self.app_state.programm_path)
        self.connect_to_emulator()

        self.click_position(736, 1324)
        time.sleep(0.5)
        screenshot = self.take_screenshot()
        position, similarity = self.find_subimage(screenshot, self.auto_image)

        if similarity > 0.8:
            self.log_message(f"Subimage found at position: {position}")
            self.click_position(position[0], position[1])
        else:
            self.click_position(736, 1324)
            screenshot = self.take_screenshot()
            position, similarity = self.find_subimage(screenshot, self.auto_image)
            if similarity > 0.8:
                self.log_message(f"Subimage found at position: {position}")
                self.click_position(position[0], position[1])

        while self.running:
            screenshot = self.take_screenshot()
            position, similarity = self.find_subimage(screenshot, self.popup_image)
            if similarity > 0.8:
                self.click_position(413, 203)

            position, similarity = self.find_subimage(screenshot, self.sell_image)

            if similarity > 0.8:
                self.log_message(f"Subimage found at position: {position}")
                self.click_position(position[0], position[1])
                time.sleep(0.5)
                screenshot = self.take_screenshot()
                if self.check_for_another_subimage(screenshot, self.cancel_image):
                    self.log_message("Another subimage found.")
                    self.perform_additional_clicks()

            time.sleep(0.5)

    def run_dungeon(self):
        """Run the dungeon."""
        os.chdir(self.app_state.programm_path)
        self.connect_to_emulator()

        screenshot = self.take_screenshot()
        position, similarity = self.find_subimage(screenshot, self.dungeon_image)

        if similarity > 0.8:
            self.log_message(f"Subimage found at position: {position}")
            self.click_position(position[0], position[1])
            time.sleep(0.5)

        while self.running:
            screenshot = self.take_screenshot()

            position, similarity = self.find_subimage(screenshot, self.enter_image)

            if similarity > 0.8:
                self.log_message(f"Subimage found at position: {position}")
                self.click_position(position[0], position[1])
                time.sleep(0.5)
                screenshot = self.take_screenshot()

                position, similarity = self.find_subimage(screenshot, self.enter_2_image)

                if similarity > 0.8:
                    self.log_message(f"Subimage found at position: {position}")
                    self.click_position(position[0], position[1])

                position, similarity = self.find_subimage(screenshot, self.challenge_image)

                if similarity > 0.8:
                    self.log_message(f"Subimage found at position: {position}")
                    self.click_position(position[0], position[1])

            time.sleep(0.5)

class AppState:
    def __init__(self):
        self.programm_path = None
        self.emulator_name = None

    def set_programm_path(self, path):
        self.programm_path = path

    def set_emulator_name(self, name):
        self.emulator_name = name


if __name__ == "__main__":
    root = tk.Tk()
    app = LegendOfMushroomBot(root)
    root.mainloop()
