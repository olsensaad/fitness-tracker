import sqlite3
from datetime import datetime

class DataManager:
    def __init__(self, db_file='workouts.db'):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """Initialize the SQLite database and create the workouts table if it doesn't exist."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                workout_type TEXT NOT NULL,
                duration INTEGER NOT NULL,
                calories INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def log_workout(self, workout_type, duration, calories):
        """
        Log a new workout to the SQLite database.
        
        Parameters:
            workout_type (str): e.g., "Run", "Walk", "Strenght"
            duration (int): Duration in minutes
            calories (int): Calories burned
        
        Returns:
            bool: True if successful, False otherwise.
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workouts (date, workout_type, duration, calories)
                VALUES (?, ?, ?, ?)
            """, (date, workout_type, duration, calories))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging workout: {e}")
            return False

    def get_past_workouts(self):
        """
        Retrieve past workouts from the SQLite database.
        
        Returns:
            list: List of tuples containing (id, date, workout_type, duration, calories)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, date, workout_type, duration, calories 
                FROM workouts 
                ORDER BY date DESC
            """)
            workouts = cursor.fetchall()
            conn.close()
            return workouts
        except Exception as e:
            print(f"Error retrieving workouts: {e}")
            return []
    
    def update_workout(self, workout_id, workout_type, duration, calories):
        """
        Update an existing workout.
        
        Parameters:
            workout_id (int): The id of the workout to update.
            workout_type (str): New workout type.
            duration (int): New duration.
            calories (int): New calories.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE workouts SET workout_type=?, duration=?, calories=? WHERE id=?
            """, (workout_type, duration, calories, workout_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating workout: {e}")
            return False

    def delete_workout(self, workout_id):
        """
        Delete a workout from the database.
        
        Parameters:
            workout_id (int): The id of the workout to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workouts WHERE id=?", (workout_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting workout: {e}")
            return False
