import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os
import random

def train_enhanced_model():
    print("Generating large enhanced synthetic dataset (2000 samples)...")
    
    np.random.seed(42)
    random.seed(42)
    
    num_samples = 2000
    
    ages = np.random.randint(18, 70, num_samples)
    heights = np.random.randint(145, 200, num_samples)
    
    # Generate weights correlated roughly with height and BMI categories
    weights = []
    for h in heights:
        # Randomly assign a BMI category to generate a realistic weight
        category = np.random.choice(['underweight', 'normal', 'overweight', 'obese'], p=[0.05, 0.45, 0.35, 0.15])
        if category == 'underweight': bmi = np.random.uniform(16, 18.5)
        elif category == 'normal': bmi = np.random.uniform(18.5, 25)
        elif category == 'overweight': bmi = np.random.uniform(25, 30)
        else: bmi = np.random.uniform(30, 40)
        
        weight = bmi * ((h/100)**2)
        weights.append(weight)
    
    weights = np.array(weights)
    goals = np.random.choice(['muscle_gain', 'weight_loss', 'maintenance', 'recomp'], num_samples)
    
    # "Keto" removed as per user request
    diet_types = np.random.choice(['veg', 'non_veg', 'vegan'], num_samples)
    
    workouts = []
    diets = []
    
    for i in range(num_samples):
        goal = goals[i]
        diet_type = diet_types[i]
        weight = weights[i]
        height = heights[i]
        age = ages[i]
        bmi = weight / ((height/100)**2)
        
        # LOGICAL WORKOUT GENERATION
        if goal == 'muscle_gain':
            if bmi < 22: # Lean, focus on mass
                workouts.append('Hypertrophy (Upper/Lower Split)')
            else: # Stronger base, focus on strength
                workouts.append('Strength (PPL Split)')
        elif goal == 'weight_loss':
            if bmi > 30: # Obese, low impact
                workouts.append('Endurance (Low-Impact LISS)')
            elif bmi > 25: # Overweight
                workouts.append('Cardio & HIIT focus')
            else: # Normal weight but wants to lose fat
                workouts.append('Metabolic Conditioning')
        elif goal == 'recomp':
            workouts.append('Functional Training & Strength')
        else: # maintenance
            if age > 50:
                workouts.append('Mobility & Light Weights')
            else:
                workouts.append('Mixed General Fitness')
                
        # LOGICAL DIET GENERATION
        if diet_type == 'vegan':
            if goal == 'muscle_gain': diets.append('High Protein Vegan')
            elif goal == 'weight_loss': diets.append('Low Calorie Vegan')
            else: diets.append('Balanced Vegan')
        elif diet_type == 'veg':
            if goal == 'muscle_gain': diets.append('High Protein Vegetarian')
            elif goal == 'weight_loss': diets.append('Low Calorie Vegetarian')
            else: diets.append('Balanced Vegetarian')
        else: # non_veg
            if goal == 'muscle_gain': diets.append('High Protein Non-Veg')
            elif goal == 'weight_loss': diets.append('Low Carb Non-Veg')
            else: diets.append('Balanced Non-Veg')

    df = pd.DataFrame({
        'age': ages,
        'weight': weights,
        'height': heights,
        'goal': goals,
        'diet_type': diet_types,
        'recommended_workout': workouts,
        'recommended_diet': diets
    })
    
    # Preprocess Categorical Data
    le_goal = LabelEncoder()
    df['goal_enc'] = le_goal.fit_transform(df['goal'])
    
    le_diet = LabelEncoder()
    df['diet_type_enc'] = le_diet.fit_transform(df['diet_type'])
    
    X = df[['age', 'weight', 'height', 'goal_enc', 'diet_type_enc']]
    y_workout = df['recommended_workout']
    y_diet = df['recommended_diet']
    
    # Train-test split for verification
    X_train, X_test, y_w_train, y_w_test = train_test_split(X, y_workout, test_size=0.2, random_state=42)
    _, _, y_d_train, y_d_test = train_test_split(X, y_diet, test_size=0.2, random_state=42)
    
    print("Training Enhanced Random Forest Classifiers...")
    workout_model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
    workout_model.fit(X_train, y_w_train)
    
    diet_model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
    diet_model.fit(X_train, y_d_train)
    
    # Verify Accuracy
    w_acc = accuracy_score(y_w_test, workout_model.predict(X_test))
    d_acc = accuracy_score(y_d_test, diet_model.predict(X_test))
    
    print(f"Workout Model Accuracy: {w_acc:.2%}")
    print(f"Diet Model Accuracy: {d_acc:.2%}")
    
    # Final fit on full data
    workout_model.fit(X, y_workout)
    diet_model.fit(X, y_diet)
    
    os.makedirs('models', exist_ok=True)
    with open('models/workout_model.pkl', 'wb') as f:
        pickle.dump(workout_model, f)
    with open('models/diet_model.pkl', 'wb') as f:
        pickle.dump(diet_model, f)
    with open('models/encoders.pkl', 'wb') as f:
        pickle.dump({'goal': le_goal, 'diet': le_diet}, f)
        
    print("Models trained and saved successfully.")

if __name__ == "__main__":
    train_enhanced_model()
