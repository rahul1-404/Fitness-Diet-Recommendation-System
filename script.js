document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('health-form');
    const inputSection = document.getElementById('input-section');
    const resultSection = document.getElementById('result-section');
    const resetBtn = document.getElementById('reset-btn');
    const generateBtn = document.getElementById('generate-btn');
    
    // Tab controls
    const tabWorkout = document.getElementById('tab-workout');
    const tabDiet = document.getElementById('tab-diet');
    const workoutSchedule = document.getElementById('workout-schedule');
    const dietSchedule = document.getElementById('diet-schedule');

    tabWorkout.addEventListener('click', () => {
        tabWorkout.classList.add('active');
        tabDiet.classList.remove('active');
        workoutSchedule.classList.remove('hidden');
        dietSchedule.classList.add('hidden');
    });

    tabDiet.addEventListener('click', () => {
        tabDiet.classList.add('active');
        tabWorkout.classList.remove('active');
        dietSchedule.classList.remove('hidden');
        workoutSchedule.classList.add('hidden');
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const age = document.getElementById('age').value;
        const weight = document.getElementById('weight').value;
        const height = document.getElementById('height').value;
        const goal = document.getElementById('goal').value;
        const diet_pref = document.getElementById('diet_pref').value;
        const gender = document.getElementById('gender').value;
        const workout_days = document.getElementById('workout_days').value;
        const weekly_goal_kg = document.getElementById('weekly_goal_kg').value;
        const activity_level = document.getElementById('activity_level').value;

        generateBtn.classList.add('loading');
        
        try {
            const response = await fetch('http://127.0.0.1:5000/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    age, weight, height, goal, diet_pref, gender, 
                    workout_days, weekly_goal_kg, activity_level 
                })
            });

            if (!response.ok) throw new Error(`API returned status ${response.status}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                // Populate Metrics
                document.getElementById('bmi-display').textContent = data.metrics.bmi;
                document.getElementById('bmr-display').textContent = data.metrics.bmr + " kcal";
                document.getElementById('calories-display').textContent = data.metrics.target_calories + " kcal";
                document.getElementById('protein-display').textContent = data.metrics.target_protein + " g";
                document.getElementById('calorie-breakdown').textContent = data.metrics.calorie_breakdown;
                
                document.getElementById('diet-type').textContent = data.diet_plan.type;
                document.getElementById('diet-strategy').textContent = data.diet_plan.strategy;
                
                document.getElementById('workout-focus').textContent = data.workout_plan.focus;
                document.getElementById('workout-frequency').textContent = data.workout_plan.frequency;

                // Render Schedules
                renderWorkout(data.workout_plan.schedule);
                renderDiet(data.diet_plan.schedule);

                // Default to Workout Tab
                tabWorkout.click();

                inputSection.classList.add('hidden');
                resultSection.classList.remove('hidden');
            } else {
                alert("Error from server: " + data.message);
            }
        } catch (error) {
            alert("Error fetching recommendation. Ensure backend is running.");
            console.error(error);
        } finally {
            generateBtn.classList.remove('loading');
        }
    });

    function renderWorkout(schedule) {
        workoutSchedule.innerHTML = '';
        const grid = document.createElement('div');
        grid.className = 'schedule-grid';
        
        schedule.forEach((day, index) => {
            const card = document.createElement('div');
            card.className = 'schedule-day-card fade-in';
            
            let tooltipHTML = '';
            if (day.details && day.details.length > 0) {
                let itemsHTML = day.details.map(ex => `
                    <div class="exercise-item">
                        <img src="${ex.media}" class="ex-img" alt="${ex.name}">
                        <div class="ex-info">
                            <div class="ex-name">${ex.name}</div>
                            <div class="ex-sets">${ex.sets} &times; ${ex.reps} Reps</div>
                        </div>
                    </div>
                `).join('');
                tooltipHTML = `<div class="day-tooltip"><h4 class="tooltip-header">Routine</h4><div class="tooltip-scroll">${itemsHTML}</div></div>`;
            }
            
            card.innerHTML = `
                <div class="day-header">${day.day}</div>
                <div class="day-body">
                    <div class="muscle-group"><strong>Focus:</strong> ${day.muscle}</div>
                    <div class="exercises"><strong>Exercises:</strong> ${day.exercises}</div>
                </div>
                ${tooltipHTML}
            `;
            grid.appendChild(card);
        });
        workoutSchedule.appendChild(grid);
    }

    function renderDiet(schedule) {
        dietSchedule.innerHTML = '';
        const grid = document.createElement('div');
        grid.className = 'schedule-grid';
        
        schedule.forEach((day, index) => {
            const card = document.createElement('div');
            card.className = 'schedule-day-card diet-card fade-in';
            
            let itemsHTML = day.meals.map(m => `
                <div class="exercise-item meal-item">
                    <div class="ex-info">
                        <div class="ex-name">${m.type}: ${m.name}</div>
                        <div class="macro-line">P: ${m.p}g | C: ${m.c}g | F: ${m.f}g</div>
                        <div class="cal-line">${m.cal} kcal</div>
                    </div>
                </div>
            `).join('');

            const tooltipHTML = `<div class="day-tooltip"><h4 class="tooltip-header">Meal Plan</h4><div class="tooltip-scroll">${itemsHTML}</div></div>`;
            
            card.innerHTML = `
                <div class="day-header">${day.day}</div>
                <div class="day-body">
                    <div class="muscle-group"><strong>Daily Totals:</strong></div>
                    <div class="diet-totals">
                        ${day.totals.cal} kcal | P: ${day.totals.p}g
                    </div>
                    <div class="exercises">Hover for meal breakdown</div>
                </div>
                ${tooltipHTML}
            `;
            grid.appendChild(card);
        });
        dietSchedule.appendChild(grid);
    }

    resetBtn.addEventListener('click', () => {
        resultSection.classList.add('hidden');
        inputSection.classList.remove('hidden');
    });
});
