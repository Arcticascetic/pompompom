# PomPomPom - Pomodoro Timer

PomPomPom is a simple desktop Pomodoro timer built with Python and Tkinter without additional dependencies. It helps you manage tasks using the Pomodoro technique, allowing you to track work sessions and breaks, and organize your tasks with a spreadsheet-like interface. Mostly vibe-coded with Gemini/CoPilot.

## Features

- Pomodoro timer with customizable work and break durations
- Task management: add, edit, and track tasks with required Pomodoros
- Save and load task lists from CSV files
- Save and load timer settings from JSON files
- Minimal, always-on-top window with draggable interface
- Right-click menu for quick actions

## Getting Started

### Prerequisites

- Python 3.x

### Installation

Clone this repository or copy the files to your local machine.

### Usage

1. Run the application:

    - ** On Windows **
        ```sh
        pythonw.exe pompompom.py
        ```
    - ** On Linux/Mac**
        ```sh
        python pompompom.py
        ```

2. Right-click on the timer window to access the menu:
    - **Next Pomodoro**: Move to the next session
    - **Pause/Resume**: Pause or resume the timer
    - **Select Task**: Choose a task to work on
    - **Task List**: Open the task spreadsheet to add/edit tasks (Do this before clicking 'Select Task'. Save the task list to update the GUI)
    - **Settings**: Adjust work/break durations and save/load settings
    - **Quit**: Exit the application

3. Manage your tasks in the spreadsheet window. Save or load your task list using CSV files. If a file named "tasks.csv" is located in the same folder, that file is loaded at start. 

4. Adjust timer durations in the settings window. Save or load your configuration using JSON files. If a file name "config.json" is located in the same folder, that file is used to overwrite the default configuration. 

## File Structure

- [`pompompom.py`](pompompom.py): Main application code
- [`tasks.csv`](tasks.csv): Example task list in CSV format

## Example Task CSV

```
Task Name,Pomodoros
Taxes,2
Accounts,2
Write,2
Design,2
Program,2
```

## License

MIT License

---
