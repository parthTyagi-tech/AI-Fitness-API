"""
utils.py
────────
Pure business-logic helpers — no Flask imports, fully testable in isolation.
"""


# ── Input validation ──────────────────────────────────────────────────────────

def validate_predict_form(form) -> tuple:
    """
    Parse and validate every field from the prediction form.
    Returns (data_dict, None) on success or (None, error_msg) on failure.
    """
    errors = []

    def _int(key, label, lo=None, hi=None):
        raw = form.get(key, '').strip()
        if not raw:
            errors.append(f"{label} is required.")
            return None
        try:
            val = int(raw)
        except ValueError:
            errors.append(f"{label} must be a whole number.")
            return None
        if lo is not None and val < lo:
            errors.append(f"{label} must be at least {lo}.")
            return None
        if hi is not None and val > hi:
            errors.append(f"{label} must be at most {hi}.")
            return None
        return val

    def _float(key, label, lo=None, hi=None):
        raw = form.get(key, '').strip()
        if not raw:
            errors.append(f"{label} is required.")
            return None
        try:
            val = float(raw)
        except ValueError:
            errors.append(f"{label} must be a number.")
            return None
        if lo is not None and val < lo:
            errors.append(f"{label} must be at least {lo}.")
            return None
        if hi is not None and val > hi:
            errors.append(f"{label} must be at most {hi}.")
            return None
        return val

    def _choice(key, label, allowed):
        raw = form.get(key, '').strip().lower()
        if raw not in allowed:
            errors.append(f"{label} has an invalid value.")
            return None
        return raw

    age      = _int  ('age',               'Age',            1,   120)
    height   = _float('height',            'Height',         50,  280)
    weight   = _float('weight',            'Weight',         20,  400)
    waist    = _float('waist_cm',          'Waist',          40,  250)
    neck     = _float('neck_cm',           'Neck',           20,  80)
    hip      = _float('hip_cm',            'Hip',            40,  250)
    sleep    = _float('sleep_hours',       'Sleep hours',    1,   24)
    calories = _float('daily_calories',    'Daily calories', 500, 10000)
    workouts = _int  ('workouts_per_week', 'Workouts/week',  0,   14)
    gender   = _choice('gender',           'Gender',         {'male', 'female'})
    activity = _choice('activity_level',   'Activity level', {'sedentary', 'light', 'moderate', 'active'})
    location = _choice('exercise_location','Exercise location', {'home', 'gym'})

    goal_raw = form.get('fitness_goal', '').strip().lower().replace(' ', '_')
    goal = goal_raw if goal_raw in {'fat_loss', 'muscle_gain', 'maintenance'} else None
    if goal is None:
        errors.append("Fitness goal has an invalid value.")

    if errors:
        return None, ' | '.join(errors)

    return {
        'age': age, 'height': height, 'weight': weight,
        'waist': waist, 'neck': neck, 'hip': hip,
        'sleep': sleep, 'calories': calories, 'workouts': workouts,
        'gender': gender, 'activity': activity, 'goal': goal,
        'exercise_location': location,
    }, None


# ── Body-fat category ─────────────────────────────────────────────────────────

def get_bf_category(bf_pct: float, gender: str) -> str:
    if gender == 'male':
        if bf_pct < 6:  return 'Essential Fat'
        if bf_pct < 14: return 'Athletes'
        if bf_pct < 18: return 'Fitness'
        if bf_pct < 25: return 'Average'
        return 'Obese'
    else:
        if bf_pct < 14: return 'Essential Fat'
        if bf_pct < 21: return 'Athletes'
        if bf_pct < 25: return 'Fitness'
        if bf_pct < 32: return 'Average'
        return 'Obese'


# ── Recommendations ───────────────────────────────────────────────────────────

def build_notes(goal: str, bf_pct: float, gender: str) -> dict:
    return {
        "bf_category": get_bf_category(bf_pct, gender),
        "goal_focus": (
            "Fat reduction and lean conditioning" if goal == "fat_loss" else
            "Strength and muscle building"        if goal == "muscle_gain" else
            "Body composition maintenance"
        ),
        "sets_reps": (
            "3-4 sets × 12-15 reps" if goal == "fat_loss" else
            "4-5 sets × 6-10 reps"  if goal == "muscle_gain" else
            "3-4 sets × 8-12 reps"
        ),
        "cardio": (
            "Add moderate cardio 3-5 times weekly." if goal == "fat_loss" else
            "Use light cardio 1-2 times weekly."    if goal == "muscle_gain" else
            "Balance cardio and strength through the week."
        ),
        "strength": "Prioritize progressive overload with proper recovery.",
        "safety":   "Maintain form, recovery, sleep, and hydration consistency.",
    }


# ── Workout split ─────────────────────────────────────────────────────────────

def build_split(workouts: int) -> list:
    if workouts <= 3:
        return ["Full Body", "Upper Body", "Lower Body"]
    if workouts == 4:
        return ["Chest & Triceps", "Back & Biceps", "Legs", "Shoulders & Core"]
    if workouts == 5:
        return ["Chest", "Back", "Legs", "Shoulders", "Arms & Core"]
    return ["Push", "Pull", "Legs", "Upper", "Lower", "Conditioning"]


# ── Exercise database ─────────────────────────────────────────────────────────
#
# Keys match the split day names returned by build_split().
# Each entry has:
#   name        – exercise name
#   sets_reps   – recommended volume
#   tip         – quick coaching cue

_GYM_EXERCISES = {
    "Full Body": [
        {"name": "Barbell Back Squat",     "sets_reps": "4 × 8-10",  "tip": "Keep chest up, knees tracking over toes"},
        {"name": "Deadlift",               "sets_reps": "3 × 6-8",   "tip": "Neutral spine, drive through heels"},
        {"name": "Bench Press",            "sets_reps": "3 × 8-10",  "tip": "Retract shoulder blades, controlled descent"},
        {"name": "Lat Pulldown",           "sets_reps": "3 × 10-12", "tip": "Pull elbows down and back, avoid momentum"},
        {"name": "Overhead Press",         "sets_reps": "3 × 8-10",  "tip": "Brace core, full lockout at top"},
        {"name": "Plank",                  "sets_reps": "3 × 45 sec","tip": "Neutral spine, squeeze glutes"},
    ],
    "Upper Body": [
        {"name": "Incline Bench Press",    "sets_reps": "4 × 8-10",  "tip": "30-45° incline, full range of motion"},
        {"name": "Barbell Row",            "sets_reps": "4 × 8-10",  "tip": "Chest parallel to floor, row to lower chest"},
        {"name": "Dumbbell Shoulder Press","sets_reps": "3 × 10-12", "tip": "Don't flare elbows, press straight up"},
        {"name": "Pull-ups",               "sets_reps": "3 × max",   "tip": "Full hang at bottom, chin over bar"},
        {"name": "Barbell Curl",           "sets_reps": "3 × 10-12", "tip": "No swinging, squeeze at top"},
        {"name": "Tricep Pushdown",        "sets_reps": "3 × 12-15", "tip": "Lock elbows at sides, full extension"},
    ],
    "Lower Body": [
        {"name": "Barbell Squat",          "sets_reps": "4 × 8-10",  "tip": "Below parallel for full glute activation"},
        {"name": "Leg Press",              "sets_reps": "4 × 10-12", "tip": "Feet shoulder width, don't lock knees"},
        {"name": "Romanian Deadlift",      "sets_reps": "3 × 10-12", "tip": "Hinge at hips, slight knee bend"},
        {"name": "Leg Curl",               "sets_reps": "3 × 12-15", "tip": "Full contraction, slow eccentric"},
        {"name": "Leg Extension",          "sets_reps": "3 × 12-15", "tip": "Pause at top, controlled descent"},
        {"name": "Standing Calf Raise",    "sets_reps": "4 × 15-20", "tip": "Full stretch at bottom, pause at top"},
    ],
    "Chest & Triceps": [
        {"name": "Flat Bench Press",       "sets_reps": "4 × 8-10",  "tip": "Arch back slightly, feet flat on floor"},
        {"name": "Incline Dumbbell Press", "sets_reps": "3 × 10-12", "tip": "Neutral grip option to protect shoulders"},
        {"name": "Cable Flye",             "sets_reps": "3 × 12-15", "tip": "Slight bend in elbows, squeeze at centre"},
        {"name": "Chest Dips",             "sets_reps": "3 × max",   "tip": "Lean forward to target chest over triceps"},
        {"name": "Skull Crushers",         "sets_reps": "3 × 10-12", "tip": "Bar to forehead, elbows stay fixed"},
        {"name": "Overhead Tricep Ext.",   "sets_reps": "3 × 12-15", "tip": "Keep elbows close to head"},
    ],
    "Back & Biceps": [
        {"name": "Deadlift",               "sets_reps": "4 × 5-6",   "tip": "Heaviest compound — treat as the anchor"},
        {"name": "Pull-ups / Lat Pulldown","sets_reps": "4 × 8-10",  "tip": "Wide grip, pull to upper chest"},
        {"name": "Seated Cable Row",       "sets_reps": "3 × 10-12", "tip": "Squeeze shoulder blades at peak"},
        {"name": "Single-Arm DB Row",      "sets_reps": "3 × 10-12", "tip": "Full stretch at bottom, no hip rotation"},
        {"name": "Barbell Curl",           "sets_reps": "3 × 10-12", "tip": "Supinate wrist at top for peak contraction"},
        {"name": "Hammer Curl",            "sets_reps": "3 × 12-15", "tip": "Neutral grip targets brachialis"},
    ],
    "Legs": [
        {"name": "Barbell Back Squat",     "sets_reps": "5 × 5",     "tip": "Brace hard, sit back not down"},
        {"name": "Leg Press",              "sets_reps": "4 × 10-12", "tip": "High foot placement = more glutes"},
        {"name": "Romanian Deadlift",      "sets_reps": "3 × 10-12", "tip": "Push hips back, keep bar close to legs"},
        {"name": "Walking Lunges",         "sets_reps": "3 × 12/leg","tip": "Long stride, front knee behind toes"},
        {"name": "Leg Curl",               "sets_reps": "3 × 12-15", "tip": "Slow eccentric for hamstring strength"},
        {"name": "Seated Calf Raise",      "sets_reps": "4 × 20",    "tip": "Targets soleus — deep calf muscle"},
    ],
    "Shoulders": [
        {"name": "Barbell Overhead Press", "sets_reps": "4 × 6-8",   "tip": "Press in a slight arc, full lockout"},
        {"name": "Dumbbell Lateral Raise", "sets_reps": "4 × 12-15", "tip": "Lead with elbows, thumb slightly down"},
        {"name": "Arnold Press",           "sets_reps": "3 × 10-12", "tip": "Rotation targets all three deltoid heads"},
        {"name": "Cable Front Raise",      "sets_reps": "3 × 12-15", "tip": "Keep arm straight, stop at shoulder height"},
        {"name": "Rear Delt Flye",         "sets_reps": "3 × 15",    "tip": "Bent over, lead with elbows out"},
        {"name": "Face Pull",              "sets_reps": "3 × 15-20", "tip": "Pull to forehead, external rotate at end"},
    ],
    "Arms & Core": [
        {"name": "Barbell Curl",           "sets_reps": "4 × 10-12", "tip": "Strict form, full range of motion"},
        {"name": "Incline DB Curl",        "sets_reps": "3 × 12",    "tip": "Long head stretch for peak bicep"},
        {"name": "Tricep Pushdown",        "sets_reps": "4 × 12-15", "tip": "Full extension, squeeze at bottom"},
        {"name": "Overhead Tricep Ext.",   "sets_reps": "3 × 12-15", "tip": "Long head emphasis"},
        {"name": "Cable Crunch",           "sets_reps": "3 × 15-20", "tip": "Round spine to crunch, not hip flexion"},
        {"name": "Hanging Leg Raise",      "sets_reps": "3 × 12-15", "tip": "Posterior pelvic tilt at top"},
    ],
    "Push": [
        {"name": "Bench Press",            "sets_reps": "4 × 6-8",   "tip": "Heavy compound to start the session"},
        {"name": "Incline DB Press",       "sets_reps": "3 × 10-12", "tip": "Targets upper chest effectively"},
        {"name": "Overhead Press",         "sets_reps": "3 × 8-10",  "tip": "Strict press, no leg drive"},
        {"name": "Lateral Raise",          "sets_reps": "3 × 15",    "tip": "Light weight, high reps for medial delt"},
        {"name": "Tricep Pushdown",        "sets_reps": "3 × 12-15", "tip": "Isolate triceps, lock elbows"},
        {"name": "Cable Flye",             "sets_reps": "3 × 15",    "tip": "Finisher — feel the stretch"},
    ],
    "Pull": [
        {"name": "Deadlift",               "sets_reps": "4 × 4-6",   "tip": "Session anchor — go heavy safely"},
        {"name": "Weighted Pull-ups",      "sets_reps": "3 × 6-8",   "tip": "Add belt weight once bodyweight is easy"},
        {"name": "Barbell Row",            "sets_reps": "3 × 8-10",  "tip": "Row to belly button for mid-back focus"},
        {"name": "Face Pull",              "sets_reps": "3 × 15-20", "tip": "Shoulder health essential"},
        {"name": "Barbell Curl",           "sets_reps": "3 × 10-12", "tip": "Strict, slow eccentric"},
        {"name": "Hammer Curl",            "sets_reps": "3 × 12",    "tip": "Brachialis for arm thickness"},
    ],
    "Upper": [
        {"name": "Incline Bench Press",    "sets_reps": "4 × 8-10",  "tip": "Upper chest priority"},
        {"name": "Lat Pulldown",           "sets_reps": "4 × 10-12", "tip": "Wide grip, chest to bar"},
        {"name": "Overhead Press",         "sets_reps": "3 × 8-10",  "tip": "Seated or standing"},
        {"name": "Cable Row",              "sets_reps": "3 × 10-12", "tip": "Squeeze at peak contraction"},
        {"name": "Lateral Raise",          "sets_reps": "3 × 15",    "tip": "Medial delt isolation"},
        {"name": "Tricep/Bicep Superset",  "sets_reps": "3 × 12 each","tip": "Pushdown + curl, minimal rest"},
    ],
    "Lower": [
        {"name": "Front Squat",            "sets_reps": "4 × 6-8",   "tip": "Quad dominant, upright torso"},
        {"name": "Romanian Deadlift",      "sets_reps": "4 × 8-10",  "tip": "Hamstring focus variation"},
        {"name": "Leg Press",              "sets_reps": "3 × 12",    "tip": "Low foot placement = quad emphasis"},
        {"name": "Bulgarian Split Squat",  "sets_reps": "3 × 10/leg","tip": "Rear foot elevated, front shin vertical"},
        {"name": "Leg Curl",               "sets_reps": "3 × 15",    "tip": "Full contraction, slow descent"},
        {"name": "Calf Raise",             "sets_reps": "4 × 20",    "tip": "Full ROM, pause at stretch"},
    ],
    "Conditioning": [
        {"name": "Battle Ropes",           "sets_reps": "4 × 30 sec","tip": "Alternate waves, stay low"},
        {"name": "Box Jumps",              "sets_reps": "4 × 8",     "tip": "Land softly, step down — don't jump down"},
        {"name": "Kettlebell Swings",      "sets_reps": "4 × 15",    "tip": "Hip hinge, not a squat"},
        {"name": "Sled Push",              "sets_reps": "4 × 20m",   "tip": "Drive from hips, lean forward"},
        {"name": "Burpees",                "sets_reps": "3 × 12",    "tip": "Chest to floor, explosive jump"},
        {"name": "Assault Bike",           "sets_reps": "3 × 45 sec","tip": "Max effort sprints, full recovery"},
    ],
}

_HOME_EXERCISES = {
    "Full Body": [
        {"name": "Burpees",                "sets_reps": "4 × 10",    "tip": "Chest to floor, explosive jump at top"},
        {"name": "Push-ups",               "sets_reps": "4 × 15-20", "tip": "Straight body line, full range"},
        {"name": "Bodyweight Squat",       "sets_reps": "4 × 20",    "tip": "Sit back, knees tracking toes"},
        {"name": "Mountain Climbers",      "sets_reps": "3 × 30 sec","tip": "Hips level, drive knees fast"},
        {"name": "Superman Hold",          "sets_reps": "3 × 12",    "tip": "Squeeze glutes and back at top"},
        {"name": "Plank",                  "sets_reps": "3 × 45 sec","tip": "Neutral spine, no sagging hips"},
    ],
    "Upper Body": [
        {"name": "Push-ups",               "sets_reps": "4 × 15-20", "tip": "Full chest to floor, elbows at 45°"},
        {"name": "Wide Push-ups",          "sets_reps": "3 × 12-15", "tip": "Wider grip targets outer chest"},
        {"name": "Diamond Push-ups",       "sets_reps": "3 × 10-12", "tip": "Hands close together, tricep focus"},
        {"name": "Pike Push-ups",          "sets_reps": "3 × 12",    "tip": "Hips high, targets shoulders"},
        {"name": "Chair Dips",             "sets_reps": "3 × 12-15", "tip": "Feet out for harder variation"},
        {"name": "Doorframe Row",          "sets_reps": "3 × 10-12", "tip": "Lean back, pull chest to frame"},
    ],
    "Lower Body": [
        {"name": "Bodyweight Squat",       "sets_reps": "4 × 20",    "tip": "Add a pause at bottom for intensity"},
        {"name": "Reverse Lunges",         "sets_reps": "3 × 12/leg","tip": "Step back, front knee stable"},
        {"name": "Glute Bridge",           "sets_reps": "4 × 15",    "tip": "Drive hips up, squeeze glutes at top"},
        {"name": "Bulgarian Split Squat",  "sets_reps": "3 × 10/leg","tip": "Rear foot on chair, front shin vertical"},
        {"name": "Wall Sit",               "sets_reps": "3 × 45 sec","tip": "90° knee angle, back flat to wall"},
        {"name": "Calf Raises",            "sets_reps": "4 × 20",    "tip": "Use a step edge for full range"},
    ],
    "Chest & Triceps": [
        {"name": "Push-ups",               "sets_reps": "4 × 15-20", "tip": "Foundation of every chest workout"},
        {"name": "Incline Push-ups",       "sets_reps": "3 × 15",    "tip": "Hands on chair — lower chest emphasis"},
        {"name": "Decline Push-ups",       "sets_reps": "3 × 12",    "tip": "Feet on chair — upper chest focus"},
        {"name": "Diamond Push-ups",       "sets_reps": "3 × 10-12", "tip": "Best bodyweight tricep exercise"},
        {"name": "Chair Dips",             "sets_reps": "3 × 12-15", "tip": "Keep body close to chair for triceps"},
        {"name": "Tricep Overhead Ext.",   "sets_reps": "3 × 12-15", "tip": "Use water bottle as weight if available"},
    ],
    "Back & Biceps": [
        {"name": "Superman",               "sets_reps": "4 × 15",    "tip": "Hold 2 sec at top, slow descent"},
        {"name": "Reverse Snow Angels",    "sets_reps": "3 × 15",    "tip": "Lying prone, arms in Y-T-W patterns"},
        {"name": "Doorframe Row",          "sets_reps": "4 × 10-12", "tip": "Feet forward, lean back, pull to chest"},
        {"name": "Resistance Band Row",    "sets_reps": "3 × 12-15", "tip": "Anchor band, pull elbows back"},
        {"name": "Resistance Band Curl",   "sets_reps": "3 × 12-15", "tip": "Stand on band, curl to shoulders"},
        {"name": "Hammer Curl (bottles)",  "sets_reps": "3 × 12",    "tip": "Use filled water bottles as weights"},
    ],
    "Legs": [
        {"name": "Jump Squats",            "sets_reps": "4 × 15",    "tip": "Explode up, soft landing, absorb impact"},
        {"name": "Walking Lunges",         "sets_reps": "3 × 12/leg","tip": "Long stride, upright torso"},
        {"name": "Single-Leg Glute Bridge","sets_reps": "3 × 12/leg","tip": "Drive through heel, full hip extension"},
        {"name": "Step-ups",               "sets_reps": "3 × 10/leg","tip": "Use stairs or sturdy chair"},
        {"name": "Lateral Lunges",         "sets_reps": "3 × 10/leg","tip": "Sit into hip, keep chest up"},
        {"name": "Calf Raises",            "sets_reps": "4 × 25",    "tip": "Use a step for full stretch at bottom"},
    ],
    "Shoulders": [
        {"name": "Pike Push-ups",          "sets_reps": "4 × 12",    "tip": "Higher hips = more shoulder load"},
        {"name": "Wall Handstand Hold",    "sets_reps": "3 × 20 sec","tip": "Work up to handstand push-ups"},
        {"name": "Lateral Raise (bottles)","sets_reps": "3 × 15",    "tip": "Lead with elbows, stop at shoulder height"},
        {"name": "Front Raise (bottles)",  "sets_reps": "3 × 15",    "tip": "Straight arm, controlled descent"},
        {"name": "Reverse Flye (bottles)", "sets_reps": "3 × 15",    "tip": "Bent over, squeeze rear delts"},
        {"name": "Arm Circles",            "sets_reps": "3 × 30 sec","tip": "Both directions, full ROM"},
    ],
    "Arms & Core": [
        {"name": "Diamond Push-ups",       "sets_reps": "4 × 12",    "tip": "Best tricep bodyweight exercise"},
        {"name": "Chair Dips",             "sets_reps": "3 × 15",    "tip": "Straight legs for harder variation"},
        {"name": "Resistance Band Curl",   "sets_reps": "4 × 12-15", "tip": "Squeeze at top, slow descent"},
        {"name": "Plank",                  "sets_reps": "3 × 60 sec","tip": "Full body tension, breathe steadily"},
        {"name": "Bicycle Crunches",       "sets_reps": "3 × 20",    "tip": "Elbow to opposite knee, slow and controlled"},
        {"name": "Leg Raises",             "sets_reps": "3 × 15",    "tip": "Lower back flat to floor throughout"},
    ],
    "Push": [
        {"name": "Push-ups",               "sets_reps": "4 × 20",    "tip": "Full ROM, squeeze chest at top"},
        {"name": "Decline Push-ups",       "sets_reps": "3 × 12-15", "tip": "Feet elevated, upper chest focus"},
        {"name": "Pike Push-ups",          "sets_reps": "3 × 12",    "tip": "Shoulder pressing pattern"},
        {"name": "Diamond Push-ups",       "sets_reps": "3 × 12",    "tip": "Tricep finisher"},
        {"name": "Lateral Raise (bottles)","sets_reps": "3 × 15",    "tip": "Medial delt isolation"},
        {"name": "Chair Dips",             "sets_reps": "3 × 12-15", "tip": "Full tricep extension at bottom"},
    ],
    "Pull": [
        {"name": "Doorframe Row",          "sets_reps": "4 × 12",    "tip": "Main back pulling movement"},
        {"name": "Superman",               "sets_reps": "4 × 15",    "tip": "Lower back and posterior chain"},
        {"name": "Resistance Band Row",    "sets_reps": "3 × 15",    "tip": "Anchor at chest height for best angle"},
        {"name": "Resistance Band Curl",   "sets_reps": "3 × 12-15", "tip": "Bicep isolation"},
        {"name": "Reverse Snow Angels",    "sets_reps": "3 × 12",    "tip": "Rear delt and trap activation"},
        {"name": "Hammer Curl (bottles)",  "sets_reps": "3 × 12",    "tip": "Brachialis and forearm thickness"},
    ],
    "Upper": [
        {"name": "Push-ups",               "sets_reps": "4 × 15-20", "tip": "Chest foundation"},
        {"name": "Doorframe Row",          "sets_reps": "4 × 12",    "tip": "Back pulling movement"},
        {"name": "Pike Push-ups",          "sets_reps": "3 × 12",    "tip": "Shoulder press alternative"},
        {"name": "Diamond Push-ups",       "sets_reps": "3 × 12",    "tip": "Tricep focus"},
        {"name": "Resistance Band Curl",   "sets_reps": "3 × 12",    "tip": "Bicep isolation"},
        {"name": "Lateral Raise (bottles)","sets_reps": "3 × 15",    "tip": "Shoulder width builder"},
    ],
    "Lower": [
        {"name": "Jump Squats",            "sets_reps": "4 × 15",    "tip": "Explosive power development"},
        {"name": "Romanian Deadlift (bottles)","sets_reps":"3 × 12", "tip": "Hip hinge, keep back flat"},
        {"name": "Reverse Lunges",         "sets_reps": "3 × 12/leg","tip": "Controlled movement, balance focus"},
        {"name": "Single-Leg Glute Bridge","sets_reps": "3 × 12/leg","tip": "Unilateral glute strength"},
        {"name": "Wall Sit",               "sets_reps": "3 × 60 sec","tip": "Isometric quad endurance"},
        {"name": "Calf Raises",            "sets_reps": "4 × 25",    "tip": "Full ROM on a step if possible"},
    ],
    "Conditioning": [
        {"name": "Burpees",                "sets_reps": "4 × 12",    "tip": "Full chest to floor, explosive jump"},
        {"name": "High Knees",             "sets_reps": "4 × 30 sec","tip": "Drive knees to hip height, pump arms"},
        {"name": "Jump Rope (or simulate)","sets_reps": "4 × 60 sec","tip": "Stay on toes, wrists drive rotation"},
        {"name": "Mountain Climbers",      "sets_reps": "3 × 30 sec","tip": "Hips level, sprint the knees in"},
        {"name": "Jump Squats",            "sets_reps": "3 × 15",    "tip": "Land soft, load the hips"},
        {"name": "Bear Crawls",            "sets_reps": "3 × 20m",   "tip": "Opposite arm-leg, hips low and level"},
    ],
}


def build_exercises(split: list, location: str) -> dict:
    """
    Returns a dict mapping each split day name to its list of exercises.
    Falls back to Full Body exercises if a day name isn't found.
    """
    db = _GYM_EXERCISES if location == 'gym' else _HOME_EXERCISES
    result = {}
    for day in split:
        result[day] = db.get(day, db.get("Full Body", []))
    return result
