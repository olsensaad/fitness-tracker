import customtkinter as ctk
from tkinter import messagebox, ttk, Menu
import pickle
import numpy as np
from tracker import DataManager

# Custom GradientFrame that draws a vertical gradient background.
class GradientFrame(ctk.CTkFrame):
    def __init__(self, master, start_color, end_color, **kwargs):
        super().__init__(master, **kwargs)
        self.start_color = start_color
        self.end_color = end_color
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        self.canvas.delete("gradient")
        (r1, g1, b1) = self.winfo_rgb(self.start_color)
        (r2, g2, b2) = self.winfo_rgb(self.end_color)
        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height
        for i in range(height):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr >> 8:02x}{ng >> 8:02x}{nb >> 8:02x}"
            self.canvas.create_line(0, i, width, i, fill=color, tags=("gradient",))
        self.canvas.lower("gradient")

class FitnessTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.title("Fitness Tracker")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Define fonts.
        self.title_font = ctk.CTkFont(family="Segoe UI", size=32, weight="bold")
        self.base_font = ctk.CTkFont(family="Segoe UI", size=18)
        
        # Initialize DataManager.
        self.data_manager = DataManager()
        
        # Load the prediction model if available.
        try:
            with open("next_exercise_model.pkl", "rb") as f:
                self.predictor = pickle.load(f)
        except Exception as e:
            self.predictor = None
            print("Prediction model not found. Train the model first.")
        
        # Create a gradient background.
        self.bg_frame = GradientFrame(self, start_color="#2A2A72", end_color="#4646A6")
        self.bg_frame.pack(fill="both", expand=True)
        
        # Create a centered card for input.
        self.card_frame = ctk.CTkFrame(self.bg_frame, fg_color="#1E1E2F", corner_radius=15)
        self.card_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
        
        self.create_widgets()
        self.update_prediction_label()
        
    def create_widgets(self):
        # Title label.
        self.title_label = ctk.CTkLabel(
            self.card_frame,
            text="Log Your Workout",
            font=self.title_font,
            text_color="white"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(30, 20))
        
        # Prediction label (new).
        self.prediction_label = ctk.CTkLabel(
            self.card_frame,
            text="Next Recommended Exercise: N/A",
            font=self.base_font,
            text_color="lightblue"
        )
        self.prediction_label.grid(row=4, column=0, columnspan=2, pady=(5, 20))
        
        # Form frame.
        self.form_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.form_frame.grid(row=1, column=0, columnspan=2, padx=40, pady=10, sticky="nsew")
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=2)
        
        # Workout Type.
        self.workout_type_label = ctk.CTkLabel(
            self.form_frame,
            text="Workout Type:",
            font=self.base_font,
            text_color="white"
        )
        self.workout_type_label.grid(row=0, column=0, sticky="e", padx=10, pady=15)
        self.workout_type_var = ctk.StringVar(value="Run")
        self.workout_type_combobox = ctk.CTkComboBox(
            self.form_frame,
            variable=self.workout_type_var,
            values=["Run", "Walk", "Strenght"],
            font=self.base_font,
            dropdown_font=self.base_font,
            width=250,
            justify="center"
        )
        self.workout_type_combobox.grid(row=0, column=1, sticky="w", padx=10, pady=15)
        
        # Duration.
        self.duration_label = ctk.CTkLabel(
            self.form_frame,
            text="Duration (min):",
            font=self.base_font,
            text_color="white"
        )
        self.duration_label.grid(row=1, column=0, sticky="e", padx=10, pady=15)
        self.duration_entry = ctk.CTkEntry(
            self.form_frame,
            font=self.base_font,
            width=250,
            placeholder_text="e.g., 30",
            justify="center"
        )
        self.duration_entry.grid(row=1, column=1, sticky="w", padx=10, pady=15)
        
        # Calories.
        self.calories_label = ctk.CTkLabel(
            self.form_frame,
            text="Calories Burned:",
            font=self.base_font,
            text_color="white"
        )
        self.calories_label.grid(row=2, column=0, sticky="e", padx=10, pady=15)
        self.calories_entry = ctk.CTkEntry(
            self.form_frame,
            font=self.base_font,
            width=250,
            placeholder_text="e.g., 250",
            justify="center"
        )
        self.calories_entry.grid(row=2, column=1, sticky="w", padx=10, pady=15)
        
        # Buttons frame.
        self.buttons_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.buttons_frame.grid(row=3, column=0, columnspan=2, padx=40, pady=(20, 30), sticky="ew")
        self.buttons_frame.columnconfigure((0, 1), weight=1)
        
        self.log_button = ctk.CTkButton(
            self.buttons_frame,
            text="Log Workout",
            command=self.log_workout,
            font=self.base_font,
            fg_color="#4646A6",
            hover_color="#3A3A8D"
        )
        self.log_button.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.view_button = ctk.CTkButton(
            self.buttons_frame,
            text="View Past Workouts",
            command=self.view_workouts,
            font=self.base_font,
            fg_color="#2A2A72",
            hover_color="#1F1F5E"
        )
        self.view_button.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        
        self.analysis_button = ctk.CTkButton(
            self.card_frame,
            text="Data Analysis",
            command=self.show_data_analysis,
            font=self.base_font,
            fg_color="#4646A6",
            hover_color="#3A3A8D"
        )
        self.analysis_button.grid(row=5, column=0, columnspan=2, padx=40, pady=(0, 30), sticky="ew")
        
    def update_prediction_label(self):
        """
        Update the next exercise prediction.
        For this simple example, we simulate a prediction using the current input.
        In a real application, you would engineer features from historical data.
        """
        if self.predictor is None:
            self.prediction_label.configure(text="Next Recommended Exercise: (Train model)")
            return
        
        # Example feature: [encoded current workout type, current duration]
        # We'll use a simple mapping for this example.
        mapping = {"Run": 0, "Walk": 1, "Strenght": 2}
        current_type = self.workout_type_var.get()
        try:
            current_duration = int(self.duration_entry.get())
        except ValueError:
            current_duration = 30  # default duration if not set
        feature = [mapping.get(current_type, 0), current_duration]
        features = np.array(feature).reshape(1, -1)
        pred_numeric = self.predictor.predict(features)[0]
        # Reverse mapping:
        reverse_mapping = {0: "Run", 1: "Walk", 2: "Strenght"}
        predicted_exercise = reverse_mapping.get(pred_numeric, "Run")
        self.prediction_label.configure(text=f"Next Recommended Exercise: {predicted_exercise}")
    
    def log_workout(self):
        workout_type = self.workout_type_var.get()
        duration = self.duration_entry.get()
        calories = self.calories_entry.get()
        
        if not workout_type or not duration or not calories:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        try:
            duration = int(duration)
            calories = int(calories)
        except ValueError:
            messagebox.showerror("Input Error", "Duration and Calories must be numbers.")
            return
        
        if self.data_manager.log_workout(workout_type, duration, calories):
            messagebox.showinfo("Success", f"Logged {workout_type} for {duration} minutes burning {calories} calories.")
            self.workout_type_var.set("Run")
            self.duration_entry.delete(0, "end")
            self.calories_entry.delete(0, "end")
            self.update_prediction_label()  # Update prediction after logging a workout.
        else:
            messagebox.showerror("Error", "Failed to log workout. Please try again.")
            
    def view_workouts(self):
        workouts = self.data_manager.get_past_workouts()
        if not workouts:
            messagebox.showinfo("No Data", "No workouts logged yet.")
            return
        
        view_window = ctk.CTkToplevel(self)
        view_window.title("Past Workouts")
        view_window.geometry("900x650")
        view_window.transient(self)
        view_window.lift()
        view_window.attributes("-topmost", True)
        view_window.after_idle(lambda: view_window.attributes("-topmost", False))
        
        title_label = ctk.CTkLabel(
            view_window,
            text="Past Workouts",
            font=self.title_font,
            text_color="white"
        )
        title_label.pack(pady=20)
        
        table_card = ctk.CTkFrame(view_window, fg_color="#1E1E2F", corner_radius=15)
        table_card.pack(padx=30, pady=20, fill="both", expand=True)
        
        style = ttk.Style(view_window)
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2A2A72",
                        fieldbackground="#2A2A72",
                        foreground="white",
                        font=("Segoe UI", 14),
                        rowheight=45)
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"))
        
        columns = ("Date", "Workout Type", "Duration (min)", "Calories")
        tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        
        for workout in workouts:
            workout_id = workout[0]
            tree.insert("", "end", iid=str(workout_id),
                        values=(workout[1], workout[2], workout[3], workout[4]))
        
        tree.bind("<Button-3>", lambda event: self.show_context_menu(event, tree))
    
    def show_context_menu(self, event, tree):
        row_id = tree.identify_row(event.y)
        if row_id:
            tree.selection_set(row_id)
            menu = Menu(tree, tearoff=0)
            menu.add_command(label="Edit", command=lambda: self.edit_workout(row_id, tree))
            menu.add_command(label="Delete", command=lambda: self.delete_workout(row_id, tree))
            menu.post(event.x_root, event.y_root)
    
    def edit_workout(self, workout_id, tree):
        current_values = tree.item(workout_id)["values"]
        if not current_values:
            return
        
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Workout")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)
        edit_window.transient(self)
        edit_window.lift()
        edit_window.attributes("-topmost", True)
        edit_window.after_idle(lambda: edit_window.attributes("-topmost", False))
        
        title = ctk.CTkLabel(edit_window, text="Edit Workout", font=self.title_font, text_color="white")
        title.pack(pady=20)
        
        form = ctk.CTkFrame(edit_window, fg_color="transparent")
        form.pack(padx=20, pady=10, fill="both", expand=True)
        
        wt_label = ctk.CTkLabel(form, text="Workout Type:", font=self.base_font, text_color="white")
        wt_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        wt_var = ctk.StringVar(value=current_values[1])
        wt_entry = ctk.CTkEntry(form, font=self.base_font, textvariable=wt_var, justify="center")
        wt_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        d_label = ctk.CTkLabel(form, text="Duration (min):", font=self.base_font, text_color="white")
        d_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        d_var = ctk.StringVar(value=str(current_values[2]))
        d_entry = ctk.CTkEntry(form, font=self.base_font, textvariable=d_var, justify="center")
        d_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        c_label = ctk.CTkLabel(form, text="Calories Burned:", font=self.base_font, text_color="white")
        c_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        c_var = ctk.StringVar(value=str(current_values[3]))
        c_entry = ctk.CTkEntry(form, font=self.base_font, textvariable=c_var, justify="center")
        c_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        def update_action():
            try:
                new_duration = int(d_var.get())
                new_calories = int(c_var.get())
            except ValueError:
                messagebox.showerror("Input Error", "Duration and Calories must be numbers.")
                return
            
            new_type = wt_var.get()
            if not new_type:
                messagebox.showwarning("Input Error", "Workout type cannot be empty.")
                return
            
            if self.data_manager.update_workout(int(workout_id), new_type, new_duration, new_calories):
                messagebox.showinfo("Success", "Workout updated successfully.")
                current_date = tree.item(workout_id)["values"][0]
                tree.item(workout_id, values=(current_date, new_type, new_duration, new_calories))
                edit_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to update workout.")
        
        update_btn = ctk.CTkButton(edit_window, text="Update Workout", command=update_action,
                                   font=self.base_font, fg_color="#4646A6", hover_color="#3A3A8D")
        update_btn.pack(pady=20)
        
    def delete_workout(self, workout_id, tree):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this workout?"):
            if self.data_manager.delete_workout(int(workout_id)):
                messagebox.showinfo("Deleted", "Workout deleted successfully.")
                tree.delete(workout_id)
            else:
                messagebox.showerror("Error", "Failed to delete workout.")
    
    def show_data_analysis(self):
        workouts = self.data_manager.get_past_workouts()
        if not workouts:
            messagebox.showinfo("No Data", "No workouts logged yet.")
            return

        analysis_window = ctk.CTkToplevel(self)
        analysis_window.title("Data Analysis")
        analysis_window.geometry("900x700")
        analysis_window.transient(self)
        analysis_window.lift()
        analysis_window.attributes("-topmost", True)
        analysis_window.after_idle(lambda: analysis_window.attributes("-topmost", False))

        # Create a filter panel with only an Exercise Type filter.
        filter_frame = ctk.CTkFrame(analysis_window, fg_color="#1E1E2F", corner_radius=10)
        filter_frame.pack(fill="x", padx=20, pady=10)

        exercise_label = ctk.CTkLabel(filter_frame, text="Exercise Type:", font=self.base_font, text_color="white")
        exercise_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        exercise_filter = ctk.CTkComboBox(filter_frame, font=self.base_font, values=["All", "Run", "Walk", "Strenght"], width=120, justify="center")
        exercise_filter.set("All")
        exercise_filter.grid(row=0, column=1, padx=5, pady=5)

        apply_btn = ctk.CTkButton(filter_frame, text="Apply Filter", font=self.base_font,
                                   fg_color="#4646A6", hover_color="#3A3A8D",
                                   command=lambda: update_plot())
        apply_btn.grid(row=0, column=2, padx=5, pady=5)

        plot_frame = ctk.CTkFrame(analysis_window, fg_color="transparent")
        plot_frame.pack(fill="both", expand=True, padx=20, pady=10)

        def update_plot():
            exercise_val = exercise_filter.get()
            filtered_workouts = []
            import datetime
            for w in workouts:
                if exercise_val != "All" and w[2] != exercise_val:
                    continue
                filtered_workouts.append(w)

            # Clear any existing plots.
            for widget in plot_frame.winfo_children():
                widget.destroy()

            filtered_dates = []
            filtered_cal_values = []
            filtered_durations = []
            total_calories_by_type = {}
            count_by_type = {}
            for w in filtered_workouts:
                try:
                    dt = datetime.datetime.strptime(w[1], "%Y-%m-%d %H:%M:%S")
                    filtered_dates.append(dt)
                    filtered_cal_values.append(w[4])
                    filtered_durations.append(w[3])
                    wt = w[2]
                    total_calories_by_type[wt] = total_calories_by_type.get(wt, 0) + w[4]
                    count_by_type[wt] = count_by_type.get(wt, 0) + 1
                except Exception as ex:
                    print("Error processing workout:", ex)
                    continue

            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.dates as mdates

            try:
                plt.style.use('seaborn-darkgrid')
            except Exception as e:
                plt.style.use('dark_background')

            fig, axs = plt.subplots(2, 2, figsize=(9, 7))
            fig.suptitle("Workout Data Analysis", fontsize=16)

            # Chart 1: Line Chart - Calories Burned Over Time
            axs[0, 0].plot(filtered_dates, filtered_cal_values, marker='o', linestyle='-', color="#4646A6")
            axs[0, 0].set_title("Calories Burned Over Time")
            axs[0, 0].set_xlabel("Date")
            axs[0, 0].set_ylabel("Calories")
            axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            fig.autofmt_xdate(rotation=45, ha='right')

            # Chart 2: Bar Chart - Total Calories by Workout Type
            types = list(total_calories_by_type.keys())
            totals = [total_calories_by_type[t] for t in types]
            axs[0, 1].bar(types, totals, color="#2A2A72")
            axs[0, 1].set_title("Total Calories by Workout Type")
            axs[0, 1].set_xlabel("Workout Type")
            axs[0, 1].set_ylabel("Total Calories")

            # Chart 3: Pie Chart - Workout Distribution
            labels = list(count_by_type.keys())
            sizes = [count_by_type[t] for t in labels]
            axs[1, 0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
                          colors=["#4646A6", "#2A2A72", "#8E44AD"])
            axs[1, 0].set_title("Workout Distribution")

            # Chart 4: Histogram - Workout Duration Distribution
            axs[1, 1].hist(filtered_durations, bins=10, color="#3A3A3C", edgecolor="white")
            axs[1, 1].set_title("Workout Duration Distribution")
            axs[1, 1].set_xlabel("Duration (min)")
            axs[1, 1].set_ylabel("Frequency")

            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        update_plot()

if __name__ == "__main__":
    app = FitnessTrackerApp()
    #retesting the version control in Github 1234
    app.mainloop()
