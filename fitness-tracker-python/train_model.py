# train_model.py
import sqlite3
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def fetch_training_data(db_file='workouts.db'):
    # Connect to your database and extract historical workout data.
    # For this simple example, let’s assume we use the previous exercise type (as an encoded value)
    # and duration as features, and the next exercise type as the label.
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT workout_type, duration FROM workouts ORDER BY date")
    data = cursor.fetchall()
    conn.close()

    # Create a very simple dataset:
    # For example, for every consecutive pair of workouts, use the first workout's type and duration as features
    # and the next workout's type as the label.
    X, y = [], []
    for i in range(len(data)-1):
        current_type, current_duration = data[i]
        next_type, _ = data[i+1]
        # Here, we need to convert the categorical workout type into a numerical value.
        # You can create a simple mapping for this example.
        mapping = {"Run": 0, "Walk": 1, "Strenght": 2}
        feature = [mapping.get(current_type, -1), current_duration]
        if feature[0] == -1:
            continue  # skip unknown types
        X.append(feature)
        y.append(mapping.get(next_type, 0))
    return np.array(X), np.array(y)

if __name__ == "__main__":
    X, y = fetch_training_data()
    if len(X) == 0:
        print("Not enough data to train the model.")
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        with open("next_exercise_model.pkl", "wb") as f:
            pickle.dump(model, f)
        print("Model trained and saved successfully.")
