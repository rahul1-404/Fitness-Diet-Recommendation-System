import os
import pickle
import pandas as pd
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

# Expanded templates for variety
DAY_TEMPLATES = {
    "Upper A": {"muscle": "Chest, Back, Arms (Power)", "exercises": "Bench Press, Barbell Rows, Overhead Press, Bicep Curls, Tricep Dips"},
    "Upper B": {"muscle": "Chest, Back, Arms (Hypertrophy)", "exercises": "Incline DB Press, Lat Pulldowns, Lateral Raises, Hammer Curls, Skull Crushers"},
    "Lower A": {"muscle": "Quads, Hamstrings, Glutes (Mass)", "exercises": "Squats, Romanian Deadlifts, Leg Press, Calf Raises"},
    "Lower B": {"muscle": "Quads, Hamstrings, Glutes (Definition)", "exercises": "Hack Squats, Lying Leg Curls, Bulgarian Split Squats, Seated Calf Raises"},
    "Full Body A": {"muscle": "Full Body (Compound focus)", "exercises": "Deadlifts, Bench Press, Pull-ups, Lunges, Planks"},
    "Full Body B": {"muscle": "Full Body (Athletic focus)", "exercises": "Clean & Press, Kettlebell Swings, Chin-ups, Box Jumps, Ab Wheel"},
    "Push A": {"muscle": "Chest, Shoulders, Triceps (Heavy)", "exercises": "Flat DB Press, Military Press, Incline Flyes, Tricep Pushdowns"},
    "Push B": {"muscle": "Chest, Shoulders, Triceps (Pump)", "exercises": "Weighted Dips, Arnold Press, Pec Deck, Overhead Extension"},
    "Pull A": {"muscle": "Back, Rear Delts, Biceps (Width)", "exercises": "Wide Grip Pull-ups, T-Bar Rows, Face Pulls, EZ Bar Curls"},
    "Pull B": {"muscle": "Back, Rear Delts, Biceps (Thickness)", "exercises": "One Arm DB Rows, Seated Cable Rows, Rear Delt Flyes, Concentration Curls"},
    "Legs A": {"muscle": "Quads & Calves", "exercises": "Front Squats, Leg Extensions, Sissy Squats, Standing Calf Raises"},
    "Legs B": {"muscle": "Hamstrings & Glutes", "exercises": "Glute Ham Raises, Stiff Leg Deadlifts, Hip Thrusts, Donkey Kicks"},
    "HIIT A": {"muscle": "Explosive Cardio", "exercises": "Burpees, Mountain Climbers, Jump Squats, Battle Ropes"},
    "HIIT B": {"muscle": "Agility Cardio", "exercises": "Sprints, Lateral Shuffles, High Knees, Plank Jacks"},
    "HIIT C": {"muscle": "Power Cardio", "exercises": "Box Jumps, Medicine Ball Slams, Speed Skaters, Tuck Jumps"},
    "LISS A": {"muscle": "Steady State (Endurance)", "exercises": "45 mins brisk walking, Light stretching"},
    "LISS B": {"muscle": "Steady State (Recovery)", "exercises": "30 mins cycling, Foam rolling"},
    "LISS C": {"muscle": "Steady State (Inclined)", "exercises": "40 mins incline treadmill walk, Hip mobility"},
    "Yoga A": {"muscle": "Flow & Flexibility", "exercises": "Sun Salutations, Warrior II, Triangle Pose, Bridge Pose"},
    "Yoga B": {"muscle": "Strength & Balance", "exercises": "Crow Pose, Tree Pose, Plank Flow, Child's Pose"},
    "Yoga C": {"muscle": "Restorative Flow", "exercises": "Pigeon Pose, Cobra Pose, Cat-Cow, Corpse Pose"},
    "Functional A": {"muscle": "Power Mechanics", "exercises": "Med Ball Slams, Turkish Get-ups, Farmer's Walk, Box Jumps"},
    "Functional B": {"muscle": "Stability Mechanics", "exercises": "Single Leg Deadlifts, Bear Crawls, Pallof Press, Bird-Dog"},
    "Functional C": {"muscle": "Coordination Mechanics", "exercises": "Lateral Band Walks, Dead Bugs, Renegade Rows, Woodchoppers"},
    "Metabolic A": {"muscle": "Fat Oxidation", "exercises": "Thrusters, Renegade Rows, Goblet Squats, Shadow Boxing"},
    "Metabolic B": {"muscle": "Conditioning", "exercises": "Rowing Machine, Kettlebell Snatches, Jump Rope, Plank to Pushup"},
    "Metabolic C": {"muscle": "Endurance Power", "exercises": "Assault Bike, Wall Balls, Double Unders, Burpees Over Bar"}
}

MEAL_DATABASE = {
    "veg": {
        "breakfast": [
            {"name": "Paneer Bhurji with Multigrain Toast", "p": 22, "c": 30, "f": 15},
            {"name": "Moong Dal Chilla (2 pcs)", "p": 18, "c": 35, "f": 8},
            {"name": "Vegetable Oats Upma", "p": 12, "c": 40, "f": 6},
            {"name": "Greek Yogurt with Mixed Nuts", "p": 20, "c": 20, "f": 12}
        ],
        "lunch": [
            {"name": "Dal Tadka with Brown Rice & Curd", "p": 24, "c": 60, "f": 12},
            {"name": "Palak Paneer with 2 Missi Rotis", "p": 30, "c": 45, "f": 18},
            {"name": "Chole (Chickpeas) with Quinoa", "p": 22, "c": 55, "f": 10},
            {"name": "Mixed Veg Sabzi with 2 Rotis", "p": 18, "c": 45, "f": 12}
        ],
        "dinner": [
            {"name": "Soya Chunks Curry with 1 Roti", "p": 35, "c": 30, "f": 8},
            {"name": "Lauki Kofta (Steamed) & Salad", "p": 15, "c": 25, "f": 8},
            {"name": "Baigan Bharta with 2 Phulkas", "p": 10, "c": 40, "f": 12},
            {"name": "Vegetable Khichdi with Moong Dal", "p": 16, "c": 50, "f": 6}
        ],
        "snacks": [
            {"name": "Roasted Makhana (1 bowl)", "p": 5, "c": 20, "f": 2},
            {"name": "Mixed Sprouts Salad", "p": 15, "c": 25, "f": 3},
            {"name": "Cottage Cheese (Paneer) Cubes", "p": 18, "c": 4, "f": 15}
        ]
    },
    "non_veg": {
        "breakfast": [
            {"name": "Egg Bhurji (3 Eggs) with 1 Roti", "p": 28, "c": 20, "f": 18},
            {"name": "Chicken Keema Paratha (Lean)", "p": 32, "c": 35, "f": 12},
            {"name": "Boiled Eggs (3) with Poha", "p": 25, "c": 45, "f": 14},
            {"name": "Omelet with Spinach & Toast", "p": 24, "c": 25, "f": 16}
        ],
        "lunch": [
            {"name": "Chicken Curry with Brown Rice", "p": 45, "c": 40, "f": 12},
            {"name": "Grilled Fish (Rohu/Surmai) & Salad", "p": 38, "c": 10, "f": 15},
            {"name": "Lean Mutton Keema with 2 Rotis", "p": 35, "c": 40, "f": 16},
            {"name": "Egg Curry (2 Eggs) with Quinoa", "p": 22, "c": 45, "f": 14}
        ],
        "dinner": [
            {"name": "Tandoori Chicken (200g) & Chutney", "p": 50, "c": 5, "f": 10},
            {"name": "Steamed Fish with Indian Spices", "p": 35, "c": 10, "f": 8},
            {"name": "Chicken Tikka (Dry) - 6 pieces", "p": 42, "c": 8, "f": 12},
            {"name": "Egg White Scramble (5 eggs) & Salad", "p": 30, "c": 8, "f": 5}
        ],
        "snacks": [
            {"name": "Grilled Chicken Strips", "p": 30, "c": 2, "f": 6},
            {"name": "Hard Boiled Eggs (2 pieces)", "p": 12, "c": 1, "f": 10},
            {"name": "Chicken Shami Kebab (Air-fried)", "p": 25, "c": 10, "f": 10}
        ]
    },
    "vegan": {
        "breakfast": [
            {"name": "Tofu Scramble with Multigrain Toast", "p": 24, "c": 30, "f": 12},
            {"name": "Ragi Dosa with Coconut Chutney", "p": 12, "c": 45, "f": 10},
            {"name": "Vegetable Poha with Toasted Peanuts", "p": 10, "c": 50, "f": 12},
            {"name": "Soy Milk Smoothie with Fruit", "p": 15, "c": 35, "f": 6}
        ],
        "lunch": [
            {"name": "Chana Masala with Brown Rice", "p": 22, "c": 65, "f": 8},
            {"name": "Rajma (Kidney Beans) with Quinoa", "p": 20, "c": 55, "f": 10},
            {"name": "Vegetable Biryani with Soy Chunks", "p": 18, "c": 60, "f": 12},
            {"name": "Yellow Moong Dal with 2 Rotis", "p": 16, "c": 50, "f": 6}
        ],
        "dinner": [
            {"name": "Tofu & Matar (Peas) Semi-dry Curry", "p": 26, "c": 20, "f": 14},
            {"name": "Kala Chana (Black Chickpeas) Curry", "p": 20, "c": 45, "f": 8},
            {"name": "Vegan Vegetable Stew with 1 Appam", "p": 12, "c": 40, "f": 10},
            {"name": "Soya & Capsicum Stir-fry", "p": 28, "c": 15, "f": 8}
        ],
        "snacks": [
            {"name": "Roasted Masala Peanuts", "p": 10, "c": 12, "f": 15},
            {"name": "Sprouted Moong Salad", "p": 15, "c": 25, "f": 2},
            {"name": "Vegan Protein Shake (Soy/Pea)", "p": 25, "c": 5, "f": 2}
        ]
    }
}

def generate_exercise_details(exercises_str):
    details = []
    exercises = [e.strip() for e in exercises_str.split(',') if e.strip()]
    for ex in exercises:
        ex_url = ex.replace(' ', '+')
        details.append({
            "name": ex,
            "sets": "3-4",
            "reps": "8-12",
            "media": f"https://placehold.co/400x250/1e293b/00f2fe?text={ex_url}"
        })
    return details

def get_schedule(workout_pred, workout_days):
    wp = workout_pred.lower()
    seq = []
    
    if "hypertrophy" in wp:
        if workout_days <= 3: seq = ["Full Body A", "Full Body B", "Full Body A"][:workout_days]
        elif workout_days == 4: seq = ["Upper A", "Lower A", "Upper B", "Lower B"]
        elif workout_days == 5: seq = ["Upper A", "Lower A", "Push A", "Pull A", "Legs A"]
        else: seq = ["Push A", "Pull A", "Legs A", "Push B", "Pull B", "Legs B"]
    elif "strength" in wp or "ppl" in wp:
        if workout_days <= 3: seq = ["Push A", "Pull A", "Legs A"][:workout_days]
        elif workout_days == 4: seq = ["Push A", "Pull A", "Legs A", "Full Body A"]
        elif workout_days == 5: seq = ["Push A", "Pull A", "Legs A", "Upper A", "Lower A"]
        else: seq = ["Push A", "Pull A", "Legs A", "Push B", "Pull B", "Legs B"]
    elif "endurance" in wp or "liss" in wp:
        seq = (["LISS A", "LISS B", "LISS C"] * 3)[:workout_days]
    elif "cardio" in wp or "hiit" in wp:
        seq = (["HIIT A", "LISS A", "HIIT B", "LISS B", "HIIT C", "LISS C"] * 2)[:workout_days]
    elif "metabolic" in wp:
        seq = (["Metabolic A", "Metabolic B", "Metabolic C"] * 3)[:workout_days]
    elif "functional" in wp:
        seq = (["Functional A", "Functional B", "Functional C"] * 3)[:workout_days]
    elif "mobility" in wp or "yoga" in wp:
        seq = (["Yoga A", "Yoga B", "Yoga C"] * 3)[:workout_days]
    else: # Fallback / Mixed
        seq = (["Full Body A", "Full Body B"] * 4)[:workout_days]

    if workout_days == 1: active_map = [1,0,0,0,0,0,0]
    elif workout_days == 2: active_map = [1,0,0,1,0,0,0]
    elif workout_days == 3: active_map = [1,0,1,0,1,0,0]
    elif workout_days == 4: active_map = [1,1,0,1,1,0,0]
    elif workout_days == 5: active_map = [1,1,0,1,1,1,0]
    elif workout_days == 6: active_map = [1,1,1,1,1,1,0]
    else: active_map = [1,1,1,1,1,1,1]
    
    schedule = []
    active_idx = 0
    for day_num in range(1, 8):
        if active_map[day_num-1] == 1 and active_idx < len(seq):
            day_type = seq[active_idx]
            template = DAY_TEMPLATES.get(day_type, DAY_TEMPLATES["Full Body A"])
            schedule.append({
                "day": f"Day {day_num} ({day_type})",
                "muscle": template["muscle"],
                "exercises": template["exercises"],
                "details": generate_exercise_details(template["exercises"])
            })
            active_idx += 1
        else:
            schedule.append({
                "day": f"Day {day_num}",
                "muscle": "Rest & Recovery",
                "exercises": "Hydration, light walk, and sleep focus.",
                "details": []
            })
    return schedule

def get_diet_schedule(diet_pred, target_cal, target_protein):
    # Determine base category
    dp = diet_pred.lower()
    category = "non_veg"
    if "vegan" in dp: category = "vegan"
    elif "veget" in dp or "veg" in dp: category = "veg"
    
    # Target per meal (approx 3 main meals + 1 snack)
    # Calorie distribution: 30% B, 30% L, 30% D, 10% S
    # Protein distribution: 25% B, 25% L, 25% D, 25% S
    
    meals_cat = MEAL_DATABASE[category]
    schedule = []
    
    for day_num in range(1, 8):
        # Pick random meals for the day
        b_base = random.choice(meals_cat["breakfast"])
        l_base = random.choice(meals_cat["lunch"])
        d_base = random.choice(meals_cat["dinner"])
        s_base = random.choice(meals_cat["snacks"])
        
        day_meals = []
        # Scaling logic: Calculate total base protein and calories
        # For simplicity, we scale each meal type to hit its target %
        meal_targets = [
            ("Breakfast", b_base, 0.30, 0.25),
            ("Lunch", l_base, 0.30, 0.25),
            ("Dinner", d_base, 0.30, 0.25),
            ("Snack", s_base, 0.10, 0.25)
        ]
        
        total_p = 0
        total_c = 0
        total_f = 0
        total_cal = 0
        
        processed_meals = []
        for m_name, base, cal_pct, p_pct in meal_targets:
            # Scale to hit protein target primarily
            target_m_p = target_protein * p_pct
            scale_p = target_m_p / base["p"]
            
            # Recalculate macros for the scaled meal
            p = round(base["p"] * scale_p, 1)
            c = round(base["c"] * scale_p, 1) # Scaling carbs/fats by same factor for texture
            f = round(base["f"] * scale_p, 1)
            cal = round(p*4 + c*4 + f*9)
            
            # Second pass: if calories are too high, trim carbs/fat
            target_m_cal = target_cal * cal_pct
            if cal > target_m_cal + 50:
                # Trim factor
                trim = target_m_cal / cal
                c = round(c * trim, 1)
                f = round(f * trim, 1)
                cal = round(p*4 + c*4 + f*9)

            processed_meals.append({
                "type": m_name,
                "name": base["name"],
                "p": p, "c": c, "f": f, "cal": cal
            })
            total_p += p
            total_c += c
            total_f += f
            total_cal += cal

        schedule.append({
            "day": f"Day {day_num}",
            "meals": processed_meals,
            "totals": {"p": round(total_p), "c": round(total_c), "f": round(total_f), "cal": round(total_cal)}
        })
        
    return schedule

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
workout_model = None
diet_model = None
encoders = None

def load_models():
    global workout_model, diet_model, encoders
    try:
        with open(os.path.join(MODELS_DIR, 'workout_model.pkl'), 'rb') as f:
            workout_model = pickle.load(f)
        with open(os.path.join(MODELS_DIR, 'diet_model.pkl'), 'rb') as f:
            diet_model = pickle.load(f)
        with open(os.path.join(MODELS_DIR, 'encoders.pkl'), 'rb') as f:
            encoders = pickle.load(f)
        print("Model state synchronized successfully.")
    except Exception as e:
        print(f"Model loading error: {e}")

load_models()

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        age = float(data.get('age', 25))
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 170))
        goal = data.get('goal', 'maintenance')
        diet_pref = data.get('diet_pref', 'veg')
        gender = data.get('gender', 'male')
        workout_days = int(data.get('workout_days', 4))
        weekly_goal_kg = float(data.get('weekly_goal_kg', 0.5))
        
        bmi = round(weight / ((height/100)**2), 2)
        if gender.lower() == 'male':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        bmr = int(round(bmr))

        # TDEE Logic (Based on explicit activity level)
        activity_factors = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "extreme": 1.9}
        activity_level = data.get('activity_level', 'moderate')
        af = activity_factors.get(activity_level, 1.375 if workout_days <= 3 else 1.55)
        tdee = bmr * af
        
        daily_diff = int(weekly_goal_kg * 1100)
        if goal == 'weight_loss': target_cal = tdee - daily_diff
        elif goal == 'muscle_gain': target_cal = tdee + daily_diff
        elif goal == 'recomp': target_cal = tdee - (daily_diff * 0.5)
        else: target_cal = tdee
        
        target_cal = int(round(target_cal))
        p_factor = 2.0 if goal == 'muscle_gain' else (1.8 if goal == 'recomp' else 1.5)
        target_protein = int(round(p_factor * weight))

        # Scientific Breakdown
        breakdown = f"BMR ({bmr}) x Activity ({af}) = TDEE ({int(tdee)} kcal). "
        if goal != 'maintenance':
            adj = "Deficit" if target_cal < tdee else "Surplus"
            breakdown += f"{adj} of {abs(int(target_cal - tdee))} kcal applied for {goal.replace('_', ' ')}."
        else:
            breakdown += "Maintenance goal selected."

        if workout_model and diet_model and encoders:
            try:
                g_enc = encoders['goal'].transform([goal])[0]
            except: g_enc = encoders['goal'].transform(['maintenance'])[0]
            try:
                d_enc = encoders['diet'].transform([diet_pref])[0]
            except: d_enc = encoders['diet'].transform(['veg'])[0]

            input_df = pd.DataFrame([{'age': age, 'weight': weight, 'height': height, 'goal_enc': g_enc, 'diet_type_enc': d_enc}])
            workout_pred = workout_model.predict(input_df)[0]
            diet_pred = diet_model.predict(input_df)[0]
        else:
            workout_pred = "Mixed General Fitness"
            diet_pred = "Balanced Diet Plan"

        workout_schedule = get_schedule(workout_pred, workout_days)
        diet_schedule = get_diet_schedule(diet_pred, target_cal, target_protein)

        return jsonify({
            "status": "success",
            "metrics": {
                "bmi": bmi, 
                "bmr": bmr, 
                "target_calories": target_cal, 
                "target_protein": target_protein, 
                "calorie_breakdown": breakdown
            },
            "diet_plan": {
                "type": diet_pred, 
                "strategy": "High protein, balanced carbs/fats.",
                "schedule": diet_schedule
            },
            "workout_plan": {"focus": workout_pred, "frequency": f"{workout_days} days/week", "schedule": workout_schedule}
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
