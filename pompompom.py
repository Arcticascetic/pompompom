import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os

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
        self.current_task = ""
        self.task_list = []
        self.current_task_index = 0

    def get_next_state(self):
        """
        Determines the next state in the Pomodoro cycle.
        """
        self.current_state_index = (self.current_state_index + 1) % len(self.pomodoro_cycle)
        state = self.pomodoro_cycle[self.current_state_index]
        if state == "Work":
            self.remaining_time = self.work_duration
            if self.task_list:
                # Move to the next task only when a work session starts
                self.current_task_index = (self.current_task_index + 1) % len(self.task_list)
                self.current_task = self.task_list[self.current_task_index][0]
            else:
                self.current_task = "No tasks"
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
        Resets the Pomodoro cycle to the initial work state.
        """
        self.current_state_index = 0
        self.remaining_time = self.work_duration
        self.is_running = False
        if self.task_list and 0 <= self.current_task_index < len(self.task_list):
            self.current_task = self.task_list[self.current_task_index][0]
        else:
            self.current_task = "No tasks"
        return self.pomodoro_cycle[self.current_state_index], self.remaining_time, self.current_task

    def select_task(self, task_index):
        """
        Selects a specific task from the task list and resets the Pomodoro.
        """
        if 0 <= task_index < len(self.task_list):
            self.current_task_index = task_index
            self.current_task = self.task_list[self.current_task_index][0]
            self.reset_pomodoro()

class PomodoroView:
    """
    Manages the graphical user interface of the Pomodoro app.
    """
    def __init__(self, root, model):
        self.root = root
        self.model = model
        self.root.title("Pomodoro")
        self.root.geometry("300x150")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.time_label = tk.Label(root, text="", font=("Helvetica", 48))
        self.time_label.pack(pady=10)

        self.state_label = tk.Label(root, text="", font=("Helvetica", 14))
        self.state_label.pack()

        self.task_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.task_label.pack()

        self.create_right_click_menu()

        # Initialize display
        state, time, task = self.model.reset_pomodoro()
        self.update_display()
        self.update_timer()

    def create_right_click_menu(self):
        """
        Creates the right-click dropdown menu.
        """
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Next Pomodoro", command=self.next_pomodoro)
        self.menu.add_command(label="Pause/Resume", command=self.pause_pomodoro)
        self.menu.add_command(label="Select Task", command=self.select_task_window)
        self.menu.add_command(label="Task List", command=self.open_task_list)

        self.root.bind("<Button-3>", self.show_menu)

    def show_menu(self, event):
        """
        Displays the right-click menu at the cursor's position.
        """
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def update_display(self):
        """
        Updates the time, state, and task labels.
        """
        mins, secs = divmod(self.model.remaining_time, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")
        self.state_label.config(text=self.model.pomodoro_cycle[self.model.current_state_index])
        self.task_label.config(text=self.model.current_task)

    def update_timer(self):
        """
        Handles the countdown logic of the timer.
        """
        if self.model.is_running and self.model.remaining_time > 0:
            self.model.remaining_time -= 1
            self.update_display()
        elif self.model.is_running and self.model.remaining_time == 0:
            self.next_pomodoro()

        self.root.after(1000, self.update_timer)

    def next_pomodoro(self):
        """
        Advances to the next state in the Pomodoro cycle.
        """
        self.model.get_next_state()
        self.update_display()

    def pause_pomodoro(self):
        """
        Pauses or resumes the Pomodoro timer.
        """
        self.model.toggle_pause()

    def select_task_window(self):
        """
        Opens a new window to select a task.
        """
        if not self.model.task_list:
            messagebox.showinfo("No Tasks", "Please load a task list first.")
            return

        select_window = tk.Toplevel(self.root)
        select_window.title("Select Task")
        select_window.attributes("-topmost", True)

        listbox = tk.Listbox(select_window, width=40)
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
        """
        Opens the task list window with an editable spreadsheet.
        """
        self.task_window = tk.Toplevel(self.root)
        self.task_window.title("Task List")
        self.task_window.attributes("-topmost", True)
        self.spreadsheet = self.create_spreadsheet(self.task_window, 20, 2)
        self.populate_spreadsheet()

        button_frame = tk.Frame(self.task_window)
        button_frame.pack()

        save_button = tk.Button(button_frame, text="Save to CSV", command=self.save_to_csv)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        load_button = tk.Button(button_frame, text="Load from CSV", command=self.load_from_csv)
        load_button.pack(side=tk.LEFT, padx=5, pady=5)

    def create_spreadsheet(self, parent, rows, cols):
        """
        Creates a simple spreadsheet using Tkinter Entry widgets.
        """
        spreadsheet_frame = tk.Frame(parent)
        spreadsheet_frame.pack(padx=10, pady=10)
        grid = []
        # Create headers
        headers = ["Task Name", "Tasklist"]
        for j, header in enumerate(headers):
            label = tk.Label(spreadsheet_frame, text=header, font=('Helvetica', 10, 'bold'))
            label.grid(row=0, column=j, sticky='nsew')

        for i in range(1, rows + 1):
            row = []
            for j in range(cols):
                entry = tk.Entry(spreadsheet_frame, width=20)
                entry.grid(row=i, column=j, sticky='nsew')
                row.append(entry)
            grid.append(row)
        return grid

    def populate_spreadsheet(self):
        """
        Populates the spreadsheet with data from the model's task list.
        """
        # Clear existing entries
        for row_entries in self.spreadsheet:
            for entry in row_entries:
                entry.delete(0, tk.END)

        # Insert new data
        for i, (task_name, pomodoros) in enumerate(self.model.task_list):
            if i < len(self.spreadsheet):
                self.spreadsheet[i][0].insert(0, task_name)
                self.spreadsheet[i][1].insert(0, pomodoros)

    def save_to_csv(self):
        """
        Saves the spreadsheet data to a CSV file and updates the model.
        """
        data = []
        for row_entries in self.spreadsheet:
            row_data = [entry.get() for entry in row_entries]
            if any(cell for cell in row_data if cell.strip()): # Only add non-empty rows
                data.append(row_data)

        # *** UPDATE THE MODEL'S TASK LIST ***
        self.model.task_list = data
        
        if self.model.task_list:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                     filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if file_path:
                try:
                    with open(file_path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(["Task Name", "Pomodoros"]) # Write header
                        writer.writerows(self.model.task_list)
                    messagebox.showinfo("Success", "Task list saved successfully.")
                    
                    # Ensure current task on display is still valid
                    self.model.select_task(self.model.current_task_index)
                    self.update_display()
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while saving: {e}")

    def load_from_csv(self):
        """
        Loads data from a CSV file into the spreadsheet and task list.
        """
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', newline='') as file:
                    reader = csv.reader(file)
                    header = next(reader) # Skip header
                    tasks = [row for row in reader]
                    
                    # *** UPDATE THE MODEL'S TASK LIST ***
                    self.model.task_list = tasks
                    self.populate_spreadsheet()
                    
                    # Reset the pomodoro to the first task
                    if self.model.task_list:
                        self.model.select_task(0)
                    else: # If CSV is empty, reset to no task
                        self.model.current_task = "No tasks"
                    self.update_display()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while loading: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    pomodoro_model = PomodoroModel()
    pomodoro_view = PomodoroView(root, pomodoro_model)
    root.mainloop()
