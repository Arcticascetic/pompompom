import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import json

class PomodoroModel:
    """
    Manages the logic of the Pomodoro timer.
    """
    def __init__(self):
        self.work_duration = 25 * 60
        self.short_break_duration = 5 * 60
        self.long_break_duration = 15 * 60
        self.pomodoro_cycle = ["Work", "Short Break", "Work", "Short Break", "Work", "Short Break", "Work", "Long Break"]
        self.current_state_index = 0
        self.is_running = False
        self.remaining_time = self.work_duration
        self.current_task = "No Task Selected"
        self.task_list = []
        self.current_task_index = -1 # Start at -1 to handle the first task correctly

    def get_next_state(self):
        """
        Determines the next state in the Pomodoro cycle.
        """
        self.current_state_index = (self.current_state_index + 1) % len(self.pomodoro_cycle)
        state = self.pomodoro_cycle[self.current_state_index]
        if state == "Work":
            self.remaining_time = self.work_duration
            if self.task_list:
                # Only advance the task index if the cycle is starting a new work session
                if self.current_state_index == 0:
                     self.current_task_index = (self.current_task_index + 1) % len(self.task_list)
                self.current_task = self.task_list[self.current_task_index][0]
            else:
                self.current_task = "No Task Selected"
        elif state == "Short Break":
            self.remaining_time = self.short_break_duration
            self.current_task = "Short Break"
        elif state == "Long Break":
            self.remaining_time = self.long_break_duration
            self.current_task = "Long Break"
        return state, self.remaining_time, self.current_task

    def toggle_pause(self):
        """
        Toggles the running state of the timer.
        """
        self.is_running = not self.is_running

    def reset_pomodoro(self):
        """
        Resets the Pomodoro cycle to the initial work state using current durations.
        """
        self.current_state_index = 0
        self.remaining_time = self.work_duration
        self.is_running = False
        if self.task_list and 0 <= self.current_task_index < len(self.task_list):
            self.current_task = self.task_list[self.current_task_index][0]
        else:
            self.current_task = "No Task Selected"
        return self.pomodoro_cycle[self.current_state_index], self.remaining_time, self.current_task

    def select_task(self, task_index):
        """
        Selects a specific task from the task list and resets the Pomodoro.
        """
        if 0 <= task_index < len(self.task_list):
            self.current_task_index = task_index
            self.reset_pomodoro()

class PomodoroView:
    """
    Manages the graphical user interface of the Pomodoro app.
    """
    def __init__(self, root, model):
        self.root = root
        self.model = model
        self.root.title("Pomodoro")
        self.root.geometry("420x150") # Adjusted window size for new layout
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        # --- NEW LAYOUT STRUCTURE ---
        # Main frame to hold all display elements
        display_frame = tk.Frame(root)
        display_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Task label on the left, with word wrapping
        self.task_label = tk.Label(display_frame, text="", font=("Helvetica", 16), justify=tk.LEFT, wraplength=180)
        self.task_label.pack(side=tk.LEFT, fill="y", padx=(0, 10))

        # Frame for timer and state on the right
        timer_state_frame = tk.Frame(display_frame)
        timer_state_frame.pack(side=tk.RIGHT, fill="y")

        # Timer and state labels packed vertically inside their frame
        self.time_label = tk.Label(timer_state_frame, text="", font=("Helvetica", 48))
        self.time_label.pack()

        self.state_label = tk.Label(timer_state_frame, text="", font=("Helvetica", 14))
        self.state_label.pack()
        # --- END OF NEW LAYOUT STRUCTURE ---

        self.create_right_click_menu()

        self.model.reset_pomodoro()
        self.update_display()
        self.update_timer()

    def create_right_click_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Next Pomodoro", command=self.next_pomodoro)
        self.menu.add_command(label="Pause/Resume", command=self.pause_pomodoro)
        self.menu.add_separator()
        self.menu.add_command(label="Select Task", command=self.select_task_window)
        self.menu.add_command(label="Task List", command=self.open_task_list)
        self.menu.add_separator()
        self.menu.add_command(label="Settings", command=self.open_settings_window)
        self.root.bind("<Button-3>", self.show_menu)

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def update_display(self):
        mins, secs = divmod(self.model.remaining_time, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")
        self.state_label.config(text=self.model.pomodoro_cycle[self.model.current_state_index])
        self.task_label.config(text=self.model.current_task)

    def update_timer(self):
        if self.model.is_running and self.model.remaining_time > 0:
            self.model.remaining_time -= 1
            self.update_display()
        elif self.model.is_running and self.model.remaining_time == 0:
            self.next_pomodoro()
        self.root.after(1000, self.update_timer)

    def next_pomodoro(self):
        self.model.get_next_state()
        self.update_display()

    def pause_pomodoro(self):
        self.model.toggle_pause()

    def select_task_window(self):
        if not self.model.task_list:
            messagebox.showinfo("No Tasks", "Please create or load a task list first.")
            return
        select_window = tk.Toplevel(self.root)
        select_window.title("Select Task")
        select_window.attributes("-topmost", True)
        listbox = tk.Listbox(select_window, width=50, height=15)
        listbox.pack(padx=10, pady=10)
        for i, task in enumerate(self.model.task_list):
            listbox.insert(tk.END, f"{i+1}. {task[0]} ({task[1]} Pomodoros)")
        def on_select():
            selected_indices = listbox.curselection()
            if selected_indices:
                self.model.select_task(selected_indices[0])
                self.update_display()
                select_window.destroy()
        select_button = tk.Button(select_window, text="Select", command=on_select)
        select_button.pack(pady=5)

    def open_task_list(self):
        self.task_window = tk.Toplevel(self.root)
        self.task_window.title("Task List")
        self.task_window.attributes("-topmost", True)
        self.spreadsheet = self.create_spreadsheet(self.task_window, 20, 2)
        self.populate_spreadsheet()
        button_frame = tk.Frame(self.task_window)
        button_frame.pack(pady=5)
        save_button = tk.Button(button_frame, text="Save to CSV", command=self.save_to_csv)
        save_button.pack(side=tk.LEFT, padx=5)
        load_button = tk.Button(button_frame, text="Load from CSV", command=self.load_from_csv)
        load_button.pack(side=tk.LEFT, padx=5)

    def create_spreadsheet(self, parent, rows, cols):
        spreadsheet_frame = tk.Frame(parent)
        spreadsheet_frame.pack(padx=10, pady=10)
        grid = []
        headers = ["Task Name", "Pomodoros"]
        for j, header in enumerate(headers):
            tk.Label(spreadsheet_frame, text=header, font=('Helvetica', 10, 'bold')).grid(row=0, column=j, sticky='nsew')
        for i in range(1, rows + 1):
            row = []
            for j in range(cols):
                entry = tk.Entry(spreadsheet_frame, width=25)
                entry.grid(row=i, column=j, sticky='nsew')
                row.append(entry)
            grid.append(row)
        return grid

    def populate_spreadsheet(self):
        for row_entries in self.spreadsheet:
            for entry in row_entries:
                entry.delete(0, tk.END)
        for i, (task_name, pomodoros) in enumerate(self.model.task_list):
            if i < len(self.spreadsheet):
                self.spreadsheet[i][0].insert(0, task_name)
                self.spreadsheet[i][1].insert(0, pomodoros)

    def save_to_csv(self):
        data = [
            [entry.get() for entry in row_entries]
            for row_entries in self.spreadsheet
            if any(entry.get().strip() for entry in row_entries)
        ]
        self.model.task_list = data
        if not self.model.task_list:
            messagebox.showwarning("Empty List", "Task list is empty. Nothing to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Task Name", "Pomodoros"])
                    writer.writerows(self.model.task_list)
                messagebox.showinfo("Success", "Task list saved.")
                if self.model.current_task_index >= len(self.model.task_list):
                    self.model.select_task(0)
                self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def load_from_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'r', newline='') as file:
                    reader = csv.reader(file)
                    next(reader) # Skip header
                    tasks = [row for row in reader if row]
                    self.model.task_list = tasks
                    self.populate_spreadsheet()
                    if self.model.task_list:
                        self.model.select_task(0)
                    else:
                        self.model.reset_pomodoro() # No tasks, just reset
                    self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {e}")

    def open_settings_window(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.attributes("-topmost", True)
        settings_window.geometry("300x200")
        frame = tk.Frame(settings_window, padx=10, pady=10)
        frame.pack(expand=True)
        tk.Label(frame, text="Work Duration (min):").grid(row=0, column=0, sticky='w', pady=5)
        tk.Label(frame, text="Short Break (min):").grid(row=1, column=0, sticky='w', pady=5)
        tk.Label(frame, text="Long Break (min):").grid(row=2, column=0, sticky='w', pady=5)
        work_var = tk.StringVar(value=str(self.model.work_duration // 60))
        short_break_var = tk.StringVar(value=str(self.model.short_break_duration // 60))
        long_break_var = tk.StringVar(value=str(self.model.long_break_duration // 60))
        entry_work = tk.Entry(frame, textvariable=work_var, width=10)
        entry_short = tk.Entry(frame, textvariable=short_break_var, width=10)
        entry_long = tk.Entry(frame, textvariable=long_break_var, width=10)
        entry_work.grid(row=0, column=1)
        entry_short.grid(row=1, column=1)
        entry_long.grid(row=2, column=1)

        def apply_settings(from_load=False):
            try:
                self.model.work_duration = int(work_var.get()) * 60
                self.model.short_break_duration = int(short_break_var.get()) * 60
                self.model.long_break_duration = int(long_break_var.get()) * 60
                self.model.reset_pomodoro()
                self.update_display()
                if not from_load:
                    settings_window.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.")
        
        def save_config_to_file():
            config_data = {'work_duration': work_var.get(), 'short_break_duration': short_break_var.get(), 'long_break_duration': long_break_var.get()}
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=4)
                messagebox.showinfo("Success", "Configuration saved.")

        def load_config_from_file():
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file_path:
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                    work_var.set(config_data['work_duration'])
                    short_break_var.set(config_data['short_break_duration'])
                    long_break_var.set(config_data['long_break_duration'])
                apply_settings(from_load=True)

        tk.Button(frame, text="Apply", command=apply_settings).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Save Config", command=save_config_to_file).grid(row=4, column=0, pady=5, sticky='ew')
        tk.Button(frame, text="Load Config", command=load_config_from_file).grid(row=4, column=1, pady=5, sticky='ew')


if __name__ == "__main__":
    root = tk.Tk()
    pomodoro_model = PomodoroModel()
    pomodoro_view = PomodoroView(root, pomodoro_model)
    root.mainloop()
