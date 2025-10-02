# MIT License

# Copyright (c) [year] [fullname]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
from tkinter import ttk  # Import the themed tkinter module
from tkinter import font as tkfont  # Import the font module
from tkinter import filedialog, messagebox
import csv
import json
import os
from typing import List, Tuple, Any, Optional

class PomodoroModel:
    """
    Manages the logic of the Pomodoro timer.
    """
    def __init__(self) -> None:
        self.work_duration: int = 25 * 60
        self.short_break_duration: int = 5 * 60
        self.long_break_duration: int = 15 * 60
        self.pomodoro_cycle: List[str] = ["Work", "Short Break", "Work", "Short Break", "Work", "Short Break", "Work", "Long Break"]
        self.current_state_index: int = 0
        self.is_running: bool = False
        self.remaining_time: int = self.work_duration
        self.current_task: str = "No Task Selected"
        self.task_list: List[List[str | int]] = []
        self.current_task_index: int = -1 # Start at -1 to handle the first task correctly

    def get_next_state(self) -> Tuple[str, int, str]:
        """
        Determines the next state in the Pomodoro cycle.
        """
        self.current_state_index = (self.current_state_index + 1) % len(self.pomodoro_cycle)
        state = self.pomodoro_cycle[self.current_state_index]
        if state == "Work":
            self.remaining_time = self.work_duration
            if self.task_list:
                if self.current_task_index == -1:
                    self.current_task_index = (self.current_task_index + 1)

                elif self.task_list[self.current_task_index][1] != 0: 
                    self.task_list[self.current_task_index][1] -= 1

                if self.task_list[self.current_task_index][1] == 0:
                    self.current_task_index = (self.current_task_index + 1) % len(self.task_list)
                
                if self.task_list[self.current_task_index][1] != 0:
                    self.current_task = self.task_list[self.current_task_index][0]
                else:
                    self.current_task = "All Tasks Completed"
            else:
                self.current_task = "No Task Selected"
        elif state == "Short Break":
            self.remaining_time = self.short_break_duration
            self.current_task = "Short Break"
        elif state == "Long Break":
            self.remaining_time = self.long_break_duration
            self.current_task = "Long Break"
        return state, self.remaining_time, self.current_task

    def start(self) -> None:
        """
        Starts the Pomodoro timer.
        """
        if not self.is_running:
            self.is_running = True


    def toggle_pause(self) -> None:
        """
        Toggles the running state of the timer.
        """
        self.is_running = not self.is_running

    def reset_pomodoro(self) -> Tuple[str, int, str]:
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

    def select_task(self, task_index: int) -> None:
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
    def __init__(self, root: tk.Tk, model: PomodoroModel) -> None:
        self.root: tk.Tk = root
        self.model: PomodoroModel = model
        self.root.title("Pomodoro")
        self.root.geometry("420x150") # Adjusted window size for new layout
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        # ---  Allow window to be resized ---
        self.root.resizable(True, True)
        self.root.minsize(120, 80) # Set a minimum practical size

        self._start_x: int = 0
        self._start_y: int = 0
        self._orig_x: int = 0
        self._orig_y: int = 0
        self._orig_width: int = 0
        self._orig_height: int = 0
        self._resizing: bool = False
        self._resize_border: int = 8  # pixels

        self.root.bind('<ButtonPress-1>', self._on_press)
        self.root.bind('<B1-Motion>', self._on_drag)
        self.root.bind('<ButtonRelease-1>', self._on_release)
        self.root.bind('<Motion>', self._on_motion)
        self.root.bind('<Configure>', self._on_resize)

        # --- Define base sizes for scaling ---
        self.base_height : int = 180
        self.base_time_font_size : int = 36
        self.base_state_font_size : int = 14
        self.base_task_font_size : int = 16
        self.height : int = 0
        self.width : int = 0

        # --- Create dynamic font objects ---
        self.time_font = tkfont.Font(family='Helvetica', size=self.base_time_font_size)
        self.state_font = tkfont.Font(family='Helvetica', size=self.base_state_font_size)
        self.task_font = tkfont.Font(family='Helvetica', size=self.base_task_font_size)

        self.root.config()

        display_frame: tk.Frame = tk.Frame(root)
        display_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.task_label: tk.Label = tk.Label(display_frame, text="", font=self.task_font, justify=tk.LEFT)
        self.task_label.pack(side=tk.LEFT, fill="y", padx=(0, 10), expand=False)

        timer_state_frame: tk.Frame = tk.Frame(display_frame)
        timer_state_frame.pack(side=tk.RIGHT, fill="y", expand=False)

        self.time_label: tk.Label = tk.Label(timer_state_frame, text="", font=self.time_font)
        self.time_label.pack(expand=True)

        self.state_label: tk.Label = tk.Label(timer_state_frame, text="", font=self.state_font)
        self.state_label.pack(expand=True)

        self.menu: Optional[tk.Menu] = None
        self.task_window: Optional[tk.Toplevel] = None
        self.spreadsheet: Optional[List[List[tk.Entry]]] = None

        self.config_filename: str = "config.json"
        self.tasks_filename: str = "tasks.csv"  

        self.create_right_click_menu()

        self.model.reset_pomodoro()
        self.update_display()
        self.update_timer()
        self.model.start()

        # Trigger it once to set initial wraplength
        self.root.update_idletasks()

    def _on_press(self, event: tk.Event) -> None:
        x, y = event.x, event.y
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        # Check if near bottom-right corner for resize
        if width - x < self._resize_border and height - y < self._resize_border:
            self._resizing = True
            self._orig_x = self.root.winfo_x()
            self._orig_y = self.root.winfo_y()
            self._orig_width = width
            self._orig_height = height
            self._start_x = event.x_root
            self._start_y = event.y_root
        else:
            self._resizing = False
            self._start_x = event.x
            self._start_y = event.y

    def _on_drag(self, event: tk.Event) -> None:
        if self._resizing:
            dx = event.x_root - self._start_x
            dy = event.y_root - self._start_y
            new_width = max(self._orig_width + dx, self.root.minsize()[0])
            new_height = max(self._orig_height + dy, self.root.minsize()[1])
            self.root.geometry(f"{int(new_width)}x{int(new_height)}")
            # print(f"Resizing: {new_width}x{new_height}")
        else:
            x = self.root.winfo_x() + (event.x - self._start_x)
            y = self.root.winfo_y() + (event.y - self._start_y)
            self.root.geometry(f"+{x}+{y}")
            # print(f"Moving to: {x},{y}")

    def _on_release(self, event: tk.Event) -> None:
        self._resizing = False

    def _on_motion(self, event: tk.Event) -> None:
        x, y = event.x, event.y
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width - x < self._resize_border and height - y < self._resize_border:
            self.root.config(cursor="bottom_right_corner")
        else:
            self.root.config(cursor="")

    # --- Method to handle window resizing and scale fonts ---
    def _on_resize(self, event):
        height : int = self.root.winfo_height()
        width : int = self.root.winfo_width()

        if width == self.width:
            return  # No change in size

        # Calculate scale factor based on height change
        scale_factor : float = height / self.base_height

        # Calculate new font sizes, with a minimum size to maintain readability
        new_time_size : int = max(8, int(self.base_time_font_size * scale_factor))
        new_state_size : int = max(6, int(self.base_state_font_size * scale_factor))
        new_task_size : int = max(7, int(self.base_task_font_size * scale_factor))

        # Configure the font objects with the new sizes
        self.time_font.config(size=new_time_size)
        self.state_font.config(size=new_state_size)
        self.task_font.config(size=new_task_size)

        # Dynamically update wraplength for the task label
        new_wraplength : int = int(width * 0.45)
        self.task_label.config(wraplength=new_wraplength)

    def create_right_click_menu(self) -> None:
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Next Pomodoro", command=self.next_pomodoro)
        self.menu.add_command(label="Pause/Resume", command=self.pause_pomodoro)
        self.menu.add_separator()
        self.menu.add_command(label="Select Task", command=self.select_task_window)
        self.menu.add_command(label="Task List", command=self.open_task_list)
        self.menu.add_separator()
        self.menu.add_command(label="Settings", command=self.open_settings_window)
        self.menu.add_separator()
        # call internal handler so we can run cleanup before destroying
        self.menu.add_command(label="Quit", command=self._on_quit)
        self.root.bind("<Button-3>", self.show_menu)

    def _on_quit(self) -> None:
        """
        Internal quit handler. If an external quit callback is set (via
        set_on_quit_callback) call it first so it can save state, then
        ensure the window is destroyed.
        """
        cb = getattr(self, "_on_quit_callback", None)
        if callable(cb):
            try:
                cb()
            except Exception as e:
                # don't crash on save error; print for debugging
                print(f"Error in quit callback: {e}")
        # Ensure window is closed
        try:
            self.root.destroy()
        except Exception:
            pass

    def set_on_quit_callback(self, callback: Optional[callable]) -> None:
        """
        Register a callback to be executed when the application quits.
        The callback should take no arguments.
        """
        self._on_quit_callback = callback

    def show_menu(self, event: tk.Event) -> None:
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def update_display(self) -> None:
        mins, secs = divmod(self.model.remaining_time, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")
        self.state_label.config(text=self.model.pomodoro_cycle[self.model.current_state_index])
        self.task_label.config(text=self.model.current_task)

    def update_timer(self) -> None:
        if self.model.is_running and self.model.remaining_time > 0:
            self.model.remaining_time -= 1
            self.update_display()
        elif self.model.is_running and self.model.remaining_time == 0:
            self.next_pomodoro()
        self.root.after(1000, self.update_timer)

    def next_pomodoro(self) -> None:
        self.model.get_next_state()
        self.update_display()

    def pause_pomodoro(self) -> None:
        self.model.toggle_pause()

    def select_task_window(self) -> None:
        if not self.model.task_list:
            messagebox.showinfo("No Tasks", "Please create or load a task list first.")
            return
        select_window: tk.Toplevel = tk.Toplevel(self.root)
        select_window.title("Select Task")
        
        listbox: tk.Listbox = tk.Listbox(select_window, width=50, height=15)
        listbox.pack(padx=10, pady=10)
        for i, task in enumerate(self.model.task_list):
            listbox.insert(tk.END, f"{i+1}. {task[0]} ({task[1]} Pomodoros)")
            
        def on_select() -> None:
            selected_indices = listbox.curselection()
            if selected_indices:
                self.model.select_task(selected_indices[0])
                self.update_display()
                select_window.destroy()
        tk.Button(select_window, text="Select", command=on_select).pack(pady=5)

    def open_task_list(self) -> None:
        self.task_window = tk.Toplevel(self.root)
        self.task_window.title("Task List")
        self.spreadsheet = self.create_spreadsheet(self.task_window, 20, 2)
        self.populate_spreadsheet()
        
        button_frame: tk.Frame = tk.Frame(self.task_window)
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="Save to CSV", command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Load from CSV", command=self.load_from_csv).pack(side=tk.LEFT, padx=5)

    def create_spreadsheet(self, parent: tk.Toplevel, rows: int, cols: int) -> List[List[tk.Entry]]:
        spreadsheet_frame: tk.Frame = tk.Frame(parent)
        spreadsheet_frame.pack(padx=10, pady=10)
        grid: List[List[tk.Entry]] = []
        headers: List[str] = ["Task Name", "Pomodoros"]
        for j, header in enumerate(headers):
            tk.Label(spreadsheet_frame, text=header, font=('Helvetica', 10, 'bold')).grid(row=0, column=j, sticky='nsew')
        for i in range(1, rows + 1):
            row: List[tk.Entry] = []
            for j in range(cols):
                entry: tk.Entry = tk.Entry(spreadsheet_frame, width=25)
                entry.grid(row=i, column=j, sticky='nsew')
                row.append(entry)
            grid.append(row)
        return grid

    def populate_spreadsheet(self) -> None:
        for row_entries in self.spreadsheet:
            for entry in row_entries:
                entry.delete(0, tk.END)
        for i, (task_name, pomodoros) in enumerate(self.model.task_list):
            if i < len(self.spreadsheet):
                self.spreadsheet[i][0].insert(0, task_name)
                self.spreadsheet[i][1].insert(0, pomodoros)

    def save_to_csv(self) -> None:

        tasks: List[List[str | int]] = []
        for row in self.spreadsheet:
            if len(row) != 2:
                raise ValueError("CSV format incorrect. Each row must have a task name and a number of pomodoros.")
            curr_task : List[List[str | int]] = []
            isValid : bool = True
            for entry in row:
                cellVal : str = entry.get()
                if len(cellVal) == 0:
                    isValid = False
                curr_task.append(cellVal)

            if isValid:
                tasks.append([curr_task[0], int(curr_task[1])])

        self.model.task_list = tasks
        if not tasks:
            messagebox.showwarning("Empty List", "Task list is empty. Nothing to save.")
            return
        file_path: str = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Task Name", "Pomodoros"])
                    writer.writerows(tasks)
                self.tasks_filename = file_path

                if self.model.current_task_index >= len(tasks): self.model.select_task(0)
                self.update_display()
                self.model.start()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def load_from_existing_csv(self, file_path: str) -> None:
        tasks: List[List[str | int]] = []
        with open(file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) != 2 or not row[1].isdigit():
                    raise ValueError("CSV format incorrect. Each row must have a task name and a number of pomodoros.")
                tasks.append([row[0], int(row[1])])
        self.model.task_list = tasks
        self.populate_spreadsheet()
        self.model.select_task(0) if tasks else self.model.reset_pomodoro()
        self.update_display()
        self.model.start()

    def load_from_csv(self) -> None:
        file_path: str = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.load_from_existing_csv(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {e}")

    def open_settings_window(self) -> None:
        settings_window: tk.Toplevel = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.attributes("-topmost", True)
        settings_window.geometry("300x200")
        
        frame: tk.Frame = tk.Frame(settings_window, padx=10, pady=10)
        frame.pack(expand=True)
        
        tk.Label(frame, text="Work Duration (min):").grid(row=0, column=0, sticky='w', pady=5)
        tk.Label(frame, text="Short Break (min):").grid(row=1, column=0, sticky='w', pady=5)
        tk.Label(frame, text="Long Break (min):").grid(row=2, column=0, sticky='w', pady=5)

        work_var: tk.StringVar = tk.StringVar(value=str(self.model.work_duration // 60))
        short_break_var: tk.StringVar = tk.StringVar(value=str(self.model.short_break_duration // 60))
        long_break_var: tk.StringVar = tk.StringVar(value=str(self.model.long_break_duration // 60))

        tk.Entry(frame, textvariable=work_var, width=10).grid(row=0, column=1)
        tk.Entry(frame, textvariable=short_break_var, width=10).grid(row=1, column=1)
        tk.Entry(frame, textvariable=long_break_var, width=10).grid(row=2, column=1)
        
        def apply_settings(from_load: bool = False) -> None:
            try:
                self.model.work_duration = int(work_var.get()) * 60
                self.model.short_break_duration = int(short_break_var.get()) * 60
                self.model.long_break_duration = int(long_break_var.get()) * 60
                self.model.reset_pomodoro()
                self.update_display()
                if not from_load: settings_window.destroy()
            except ValueError: messagebox.showerror("Invalid Input", "Please enter valid numbers.")
        
        def save_config() -> None:
            data = {'work': work_var.get(), 'short': short_break_var.get(), 'long': long_break_var.get()}
            path: str = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if path:
                with open(path, 'w') as f: json.dump(data, f, indent=4)
                self.config_filename = path

        def load_config() -> None:
            path: str = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if path:
                with open(path, 'r') as f: data = json.load(f)
                work_var.set(data['work'])
                short_break_var.set(data['short'])
                long_break_var.set(data['long'])
                apply_settings(from_load=True)

        tk.Button(frame, text="Apply", command=apply_settings).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Save Config", command=save_config).grid(row=4, column=0, pady=5, sticky='ew')
        tk.Button(frame, text="Load Config", command=load_config).grid(row=4, column=1, pady=5, sticky='ew')

if __name__ == "__main__":
    root: tk.Tk = tk.Tk()
    root.withdraw() 
    
    # Create model and view
    pomodoro_model: PomodoroModel = PomodoroModel()
    pomodoro_view: PomodoroView = PomodoroView(root, pomodoro_model)

    def on_close() -> None:
        """Save config.json and tasks.csv in the current folder, then exit."""
        # Save config.json (store durations in minutes as strings to match GUI format)
        try:
            config_data = {
                'work': str(pomodoro_model.work_duration // 60),
                'short': str(pomodoro_model.short_break_duration // 60),
                'long': str(pomodoro_model.long_break_duration // 60),
            }
            with open(pomodoro_view.config_filename, "w") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config.json: {e}")

        # Save tasks.csv (only non-empty task list entries)
        try:
            tasks = pomodoro_model.task_list
            with open(pomodoro_view.tasks_filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Task Name", "Pomodoros"])
                for row in tasks:
                    # Expect rows like [name, count]
                    if not row:
                        continue
                    name = str(row[0])
                    count = row[1] if len(row) > 1 else ""
                    writer.writerow([name, count])
        except Exception as e:
            print(f"Error saving tasks.csv: {e}")

        # Finalize exit
        try:
            root.destroy()
        except Exception:
            pass

    # Register quit callback on the view and the window manager close protocol
    pomodoro_view.set_on_quit_callback(on_close)
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    # Try to load configuration
    if os.path.exists(pomodoro_view.config_filename):
        try:
            with open(pomodoro_view.config_filename, 'r') as f:
                data : dict = json.load(f)
                pomodoro_model.work_duration = int(data['work']) * 60
                pomodoro_model.short_break_duration = int(data['short']) * 60
                pomodoro_model.long_break_duration = int(data['long']) * 60
                pomodoro_model.reset_pomodoro()
                pomodoro_view.update_display()
        except Exception as e:
            print(f"Error loading config.json: {e}")
    
    # Try to load tasks
    if os.path.exists(pomodoro_view.tasks_filename):
        try:
            pomodoro_view.load_from_existing_csv(pomodoro_view.tasks_filename)
        except Exception as e:
            print(f"Error loading tasks.csv: {e}")
    
    root.deiconify() 
    root.mainloop()
