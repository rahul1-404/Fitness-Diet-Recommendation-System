import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/recommend"

test_cases = [
    {
        "name": "Sedentary Maintenance (Male)",
        "data": {
            "age": 25, "weight": 70, "height": 170, "goal": "maintenance", 
            "diet_pref": "veg", "gender": "male", "workout_days": 1, "weekly_goal_kg": 0,
            "activity_level": "sedentary"
        }
    },
    {
        "name": "Active Muscle Gain (Female)",
        "data": {
            "age": 28, "weight": 60, "height": 165, "goal": "muscle_gain", 
            "diet_pref": "non_veg", "gender": "female", "workout_days": 5, "weekly_goal_kg": 0.5,
            "activity_level": "active"
        }
    }
]

def verify():
    print("Final Verification (Activity Level + Detailed Breakdown)...")
    print("-" * 70)
    
    for case in test_cases:
        print(f"Testing Case: {case['name']}")
        try:
            response = requests.post(BASE_URL, json=case['data'])
            if response.status_code == 200:
                res = response.json()
                t_cal = res['metrics']['target_calories']
                breakdown = res['metrics']['calorie_breakdown']
                
                print(f"  Target: {t_cal} kcal")
                print(f"  Breakdown: {breakdown}")
                
                # Check macro scaling for Day 1
                d1 = res['diet_plan']['schedule'][0]
                d1_cal = d1['totals']['cal']
                d1_p = d1['totals']['p']
                print(f"  [PASS] Day 1: {d1_cal} kcal | {d1_p}g Protein")
                
            else:
                print(f"  [FAIL] Status Code: {response.status_code}")
        except Exception as e:
            print(f"  [ERROR] Connection failed: {e}")
        print("-" * 70)

if __name__ == "__main__":
    verify()
