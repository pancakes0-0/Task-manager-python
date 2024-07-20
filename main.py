import customtkinter as ctk
from tkinter import messagebox
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class Task:
    def __init__(self, title, description, due_date, priority, status="Pending"):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "priority": self.priority,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(
            data["title"],
            data["description"],
            datetime.strptime(data["due_date"], "%Y-%m-%d"),
            data["priority"],
            data["status"]
        )
        return task

class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advanced Task Manager")
        self.geometry("1000x800")

        self.tasks = []
        self.load_tasks()

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for task list and inputs
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # Right frame for statistics and charts
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # Task input fields
        self.title_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Task Title")
        self.title_entry.pack(fill=ctk.X, padx=5, pady=2)

        self.description_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Task Description")
        self.description_entry.pack(fill=ctk.X, padx=5, pady=2)

        self.due_date_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Due Date (YYYY-MM-DD)")
        self.due_date_entry.pack(fill=ctk.X, padx=5, pady=2)

        self.priority_var = ctk.StringVar(value="Medium")
        self.priority_menu = ctk.CTkOptionMenu(self.left_frame, values=["Low", "Medium", "High"], variable=self.priority_var)
        self.priority_menu.pack(fill=ctk.X, padx=5, pady=2)

        self.add_button = ctk.CTkButton(self.left_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(fill=ctk.X, padx=5, pady=5)

        # Task list tabs
        self.task_tabs = ctk.CTkTabview(self.left_frame)
        self.task_tabs.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        self.pending_tab = self.task_tabs.add("Pending Tasks")
        self.completed_tab = self.task_tabs.add("Completed Tasks")

        # Task lists
        self.pending_task_list = ctk.CTkScrollableFrame(self.pending_tab, width=350, height=300)
        self.pending_task_list.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        self.completed_task_list = ctk.CTkScrollableFrame(self.completed_tab, width=350, height=300)
        self.completed_task_list.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # Statistics labels
        self.stats_frame = ctk.CTkFrame(self.right_frame)
        self.stats_frame.pack(fill=ctk.X, padx=5, pady=5)

        self.total_tasks_label = ctk.CTkLabel(self.stats_frame, text="Total Tasks: 0")
        self.total_tasks_label.pack(anchor=ctk.W)

        self.pending_tasks_label = ctk.CTkLabel(self.stats_frame, text="Pending Tasks: 0")
        self.pending_tasks_label.pack(anchor=ctk.W)

        self.completed_tasks_label = ctk.CTkLabel(self.stats_frame, text="Completed Tasks: 0")
        self.completed_tasks_label.pack(anchor=ctk.W)

        # Chart
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        self.update_task_list()
        self.update_statistics()
        self.update_chart()

    def add_task(self):
        title = self.title_entry.get()
        description = self.description_entry.get()
        due_date_str = self.due_date_entry.get()
        priority = self.priority_var.get()

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        task = Task(title, description, due_date, priority)
        self.tasks.append(task)

        self.clear_inputs()
        self.update_task_list()
        self.update_statistics()
        self.update_chart()
        self.save_tasks()

    def clear_inputs(self):
        self.title_entry.delete(0, ctk.END)
        self.description_entry.delete(0, ctk.END)
        self.due_date_entry.delete(0, ctk.END)
        self.priority_var.set("Medium")

    def update_task_list(self):
        # Clear existing tasks
        for widget in self.pending_task_list.winfo_children():
            widget.destroy()
        for widget in self.completed_task_list.winfo_children():
            widget.destroy()

        # Add tasks to appropriate lists
        for index, task in enumerate(self.tasks):
            if task.status == "Pending":
                self.create_task_widget(self.pending_task_list, task, index)
            else:
                self.create_task_widget(self.completed_task_list, task, index)

    def create_task_widget(self, parent, task, index):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill=ctk.X, padx=5, pady=5)

        title_label = ctk.CTkLabel(frame, text=f"{task.title} - Due: {task.due_date.strftime('%Y-%m-%d')} - Priority: {task.priority}")
        title_label.pack(side=ctk.LEFT, padx=5)

        if task.status == "Pending":
            complete_button = ctk.CTkButton(frame, text="Complete", width=80, command=lambda: self.complete_task(index))
            complete_button.pack(side=ctk.RIGHT, padx=5)

        status_label = ctk.CTkLabel(frame, text=f"Status: {task.status}")
        status_label.pack(side=ctk.RIGHT, padx=5)

    def complete_task(self, index):
        self.tasks[index].status = "Completed"
        self.update_task_list()
        self.update_statistics()
        self.update_chart()
        self.save_tasks()

    def update_statistics(self):
        total_tasks = len(self.tasks)
        pending_tasks = sum(1 for task in self.tasks if task.status == "Pending")
        completed_tasks = total_tasks - pending_tasks

        self.total_tasks_label.configure(text=f"Total Tasks: {total_tasks}")
        self.pending_tasks_label.configure(text=f"Pending Tasks: {pending_tasks}")
        self.completed_tasks_label.configure(text=f"Completed Tasks: {completed_tasks}")

    def update_chart(self):
        self.ax.clear()
        priorities = ["Low", "Medium", "High"]
        pending_counts = [sum(1 for task in self.tasks if task.priority == p and task.status == "Pending") for p in priorities]
        completed_counts = [sum(1 for task in self.tasks if task.priority == p and task.status == "Completed") for p in priorities]

        x = range(len(priorities))
        width = 0.35

        self.ax.bar([i - width/2 for i in x], pending_counts, width, label='Pending', color='#FFA500')
        self.ax.bar([i + width/2 for i in x], completed_counts, width, label='Completed', color='#4CAF50')

        self.ax.set_ylabel('Number of Tasks')
        self.ax.set_title('Tasks by Priority and Status')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(priorities)
        self.ax.legend()

        self.canvas.draw()

    def save_tasks(self):
        with open("tasks.json", "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f)

    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                task_data = json.load(f)
                self.tasks = [Task.from_dict(data) for data in task_data]
        except FileNotFoundError:
            self.tasks = []

if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()