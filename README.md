<div align="center">

<br/>


# AI Driven Fitness Intelligence System

**Your Body. Decoded.**

<br/>

[![Live Demo](https://img.shields.io/badge/🚀%20LIVE%20DEMO-ai--fitness--api.onrender.com-d2494b?style=for-the-badge&labelColor=0a0a0a)](https://ai-fitness-api-68n1.onrender.com)
&nbsp;
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)](https://python.org)
&nbsp;
[![Flask](https://img.shields.io/badge/Flask-Backend-ffffff?style=for-the-badge&logo=flask&logoColor=white&labelColor=0a0a0a)](https://flask.palletsprojects.com)
&nbsp;
[![ML](https://img.shields.io/badge/Scikit--Learn-ML%20Engine-f7931e?style=for-the-badge&logo=scikit-learn&logoColor=white&labelColor=0a0a0a)](https://scikit-learn.org)
&nbsp;
[![GitHub Stars](https://img.shields.io/github/stars/ParthTyagi?style=for-the-badge&color=ffd700&labelColor=0a0a0a&logo=github)](https://github.com/ParthTyagi)

<br/>

> A production-grade, full-stack fitness intelligence platform powered by machine learning.  
> Input 12+ biometric data points → get real-time body fat predictions, personalised workout splits, and goal-aligned training recommendations — all inside a sleek, animated dark UI.

<br/>

</div>

---

## 📸 Live Screenshots

<br/>

### 🔐 Login — Secure Access Terminal

> Two-column layout: feature overview on the left, neumorphic dark card with full auth flow on the right. Three.js animated gym equipment renders in the background.

![Login Page](https://github.com/user-attachments/assets/1c913664-8143-47b3-9102-5f0232c55c65)

<br/>

---

### 🧬 Biometric Analysis Form — ML Input Terminal

> 12-field biometric form with section dividers, neumorphic inputs, and a pill-shaped animated submit button. Auto-populates from saved user profile.

![Prediction Form](https://github.com/user-attachments/assets/1fc09b76-aa98-4a45-8d27-25db39d5077a)

<br/>

---

### 📊 Analysis Results — Real-Time ML Output

> Instantly displays predicted body fat %, fitness category, animated gauge bar, biometric chips, side metric cards, and workout frequency — all driven by the ML engine.

![Results Page](https://github.com/user-attachments/assets/7278b841-05c1-4dad-8c27-bb4b04e48f59)

<br/>

---

### 🗂️ Dashboard — Intelligence Command Center

> Profile card with avatar, status indicator, full prediction history table, and record count — all in one view.

![Dashboard](https://github.com/user-attachments/assets/dfc09ea4-e319-4d49-ace9-2e7aee68a1f2)

<br/>

---

## ⚡ Key Stats

<div align="center">

|  Metric | Value |
|---------|-------|
| 📥 Biometric inputs analysed | **12+** |
| 🎯 ML prediction accuracy | **Real-time** |
| 📂 Pages / modules | **6** |
| 🔐 Auth flows | **Login · Register · Reset** |
| 🏋️ Workout splits generated | **Custom per user** |
| ☁️ Hosting | **Render (live)** |

</div>

<br/>

---

## ✨ Feature Overview

<br/>

```
╔══════════════════════════╦════════════════════════════════════════════════════╦════════╗
║  Module                  ║  Description                                       ║ Status ║
╠══════════════════════════╬════════════════════════════════════════════════════╬════════╣
║  ⚡ ML Prediction Engine  ║  Body fat % from 12+ biometric inputs              ║  ✅    ║
║  🧬 Biometric Analysis   ║  Age · Weight · Height · Waist · Neck · Hip + more ║  ✅    ║
║  🎯 Workout Splits       ║  Custom weekly splits aligned to your goal          ║  ✅    ║
║  📊 History Tracking     ║  Full prediction log per user, newest-first         ║  ✅    ║
║  💡 Smart Recommendations║  Cardio, sets/reps, safety & strength notes         ║  ✅    ║
║  🔐 Auth System          ║  Login · Register · Password Recovery               ║  ✅    ║
║  📱 Responsive UI        ║  Dark neumorphic design, Three.js 3D background     ║  ✅    ║
╚══════════════════════════╩════════════════════════════════════════════════════╩════════╝
```

<br/>

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   User enters 12+ biometric data points via the web form        │
│   (age, height, weight, waist, neck, hip, sleep, workouts...)   │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │  POST /predict
                             ▼
              ┌──────────────────────────┐
              │       Flask Backend      │
              │  · Auth & session mgmt   │
              │  · Input validation      │
              │  · History persistence   │
              └──────────────┬───────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │    Scikit-Learn Model    │
              │  · Trained regression    │
              │  · Predicts body fat %   │
              │  · Classifies category   │
              └──────────────┬───────────┘
                             │
                             ▼
              ┌──────────────────────────────────────┐
              │    Personalised Output Engine         │
              │  · Body fat % + fitness category      │
              │  · Animated gauge bar (0–50%)          │
              │  · Custom weekly workout split         │
              │  · Goal-focused training notes         │
              │  · Cardio, sets/reps, safety advice    │
              └──────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   Dashboard + History    │
              │  · Auto-saved per user   │
              │  · Full data table view  │
              └──────────────────────────┘
```

<br/>

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, CSS3, Vanilla JS | Pages & animations |
| **3D Background** | Three.js (r128) | Animated gym equipment scene |
| **Templating** | Jinja2 | Dynamic server-side rendering |
| **Backend** | Python 3.10+, Flask | API, routing, auth |
| **ML Engine** | Scikit-learn, Pandas, NumPy | Body fat prediction model |
| **Database** | SQLite + SQLAlchemy | User data & prediction history |
| **Auth** | Flask-Login, Werkzeug | Secure session management |
| **Hosting** | Render | Live deployment |

</div>

<br/>

---

## 🧬 Biometric Inputs Analysed

The ML engine processes the following **12+ data points**:

```
Physical Profile          Measurements              Lifestyle & Activity
─────────────────         ─────────────────         ──────────────────────
• Age                     • Weight (kg)             • Activity Level
• Height (cm)             • Waist circumference     • Workouts per week
• Gender                  • Neck circumference      • Sleep hours per day
                          • Hip circumference       • Daily caloric intake
                                                    • Fitness Goal
                                                    • Training Location
```

<br/>

---

## 🎨 UI Design System

The entire frontend is built around a **dark neumorphic design language**:

- **Colour palette** — Pure black `#0a0a0a` base · dark grey cards `#121212` · red accent `#d2494b`
- **3D background** — Three.js floating gym equipment (dumbbells, barbells, kettlebells, weight plates) with mouse-parallax
- **Inputs** — Neumorphic inset shadow fields: `6px 6px 10px rgba(0,0,0,1)` with scale-on-focus
- **Buttons** — Pill-shaped gradient buttons with inner circular icon, active press depth, and a red SVG loader animation on submit
- **Cards** — `inset 2px 2px 10px rgba(0,0,0,1)` + `inset -1px -1px 5px rgba(255,255,255,0.06)` glass panels
- **Login** — 3D flip card (CSS `transform-style: preserve-3d`) toggling between Login and Register faces
- **Typography** — Barlow Condensed (headings) + Exo 2 (body) from Google Fonts

<br/>

---

## 🚀 Getting Started

### Prerequisites

```
Python 3.10+
pip
Git
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ParthTyagi/ai-fitness-api.git
cd ai-fitness-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open **`http://localhost:5000`** in your browser. 🎉

<br/>

---

## 🤖 Machine Learning Model & 5-Fold Cross-Validation

The core engine is an end-to-end scikit-learn Pipeline with:
1. **Leak-Free Outlier Handling (`OutlierHandler`)**: Fits IQR & 3-sigma bounds strictly on training data during `.fit()`, preventing data leakage and eliminating hardcoded constants.
2. **Biometric Feature Engineering (`FeatureEngineer`)**: Calculates Body Mass Index (BMI), Waist-to-Hip Ratio (WHR), and Waist-to-Height Ratio (WHtR).
3. **Preprocessing (`ColumnTransformer`)**: `OneHotEncoder(handle_unknown='ignore', drop='first')` for categorical variables (`gender`, `fitness_goal`), `OrdinalEncoder` for `activity_level`, and `StandardScaler` for all numerical features.
4. **Gradient Boosted Tree (`XGBRegressor`)**: Hyperparameter tuned via `RandomizedSearchCV` with early stopping.

### 5-Fold Cross-Validation Benchmark Comparison

<div align="center">

| Model | Feature Engineering | $R^2$ Score | MAE (%) | RMSE (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Linear Regression** (Baseline) | None | $0.9890 \pm 0.0015$ | $0.3085 \pm 0.0119$ | $0.4604 \pm 0.0316$ |
| **Linear Regression** (Enhanced) | BMI, WHR, WHtR | $0.9984 \pm 0.0012$ | $0.0380 \pm 0.0032$ | $0.1642 \pm 0.0592$ |
| **XGBoost Regressor** (Default) | None | $0.9944 \pm 0.0018$ | $0.2100 \pm 0.0099$ | $0.3263 \pm 0.0503$ |
| **XGBoost Regressor** (Tuned Production) | BMI, WHR, WHtR | **$0.9974 \pm 0.0018$** | **$0.0711 \pm 0.0074$** | **$0.2122 \pm 0.0700$** |

</div>

*Evaluated with 5-fold cross-validation (`KFold(n_splits=5, shuffle=True, random_state=42)`).*

<br/>

---

## 📂 Project Structure

```
ai-fitness-api/
│
├── app.py                        # FastAPI application, lifespan, session middleware & ASGI entry point
├── routes.py                     # Main router: prediction endpoints, guest flows & OAuth
├── database.py                   # SQLAlchemy 2.0 engine, SessionLocal & init_db
├── db_models.py                  # Declarative SQLAlchemy models (User, Result, UserProfile)
├── templates.py                  # Jinja2Templates configuration, url_for, flash & CSRF helpers
├── auth.py                       # Auth dependencies (get_current_user, login_required, verify_csrf)
├── utils.py                      # Pure business logic, token serializer, exercises & validation
├── extensions.py                 # Starlette OAuth client configuration
│
├── models/
│   └── gym_ai_bodyfat_model.pkl  # Trained production ML pipeline (Joblib)
│
├── templates/
│   ├── login.html                # Two-column auth page + Three.js bg (CSRF protected)
│   ├── register.html             # 3D flip card (login ↔ register, CSRF protected)
│   ├── guest_form.html           # Free guest intake form (CSRF protected)
│   ├── index.html                # Biometric analysis form (12+ fields, CSRF protected)
│   ├── result.html               # ML results + workout split + warning banner
│   ├── dashboard.html            # Profile card + prediction history table + account deletion
│   ├── reset_password.html       # Time-limited token password recovery (30m expiry)
│   ├── 404.html                  # Custom 404 Not Found error view
│   └── 500.html                  # Custom 500 Server Error view
│
├── static/
│   └── images/
│       ├── bg.jpg                # Gym background image
│       └── style.css             # Supplementary stylesheet
│
├── runtime.txt                   # Pinned python-3.11.9 runtime for Render
├── start_01.ipynb                # End-to-end ML training, CV benchmark & tuning notebook
├── fitness_dataset_5000.csv      # 5,000 participant training dataset
├── requirements.txt              # Production dependency specifications (FastAPI, Uvicorn, Psycopg)
└── README.md
```

<br/>

---

## 🗺️ Roadmap

- [x] ML body fat prediction engine (real-time)
- [x] 12+ biometric input form with standardized choice sets
- [x] Token-based signed password reset (`itsdangerous`, 30-minute expiry)
- [x] Complete CSRF protection via Flask-WTF
- [x] User authentication — login / register / Google OAuth 2.0
- [x] Prediction history tracking (per-user, timestamped)
- [x] Custom weekly workout split generation (Home / Gym)
- [x] Goal-aligned training notes (cardio, sets/reps, safety)
- [x] Three.js animated 3D background
- [x] Neumorphic dark UI design system
- [x] 5-Fold Cross Validation & XGBoost Hyperparameter Tuning
- [ ] Progress charts (Chart.js / D3)
- [ ] Nutrition & macro recommendations
- [ ] Mobile app (React Native)
- [ ] Wearable integration (Fitbit, Apple Watch)
- [ ] REST API + Swagger documentation
- [ ] Multi-language support

<br/>

---

## 🤝 Contributing

Contributions, issues, and feature requests are always welcome!

```bash
# 1. Fork the project
# 2. Create your feature branch
git checkout -b feature/YourFeatureName

# 3. Commit your changes
git commit -m "Add: YourFeatureName"

# 4. Push to GitHub
git push origin feature/YourFeatureName

# 5. Open a Pull Request
```

<br/>

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

<br/>

---

<div align="center">

```
╔══════════════════════════════════════════════╗
║                                              ║
║   Developed with 💪 by  Parth Tyagi          ║
║   github.com/ParthTyagi                      ║
║                                              ║
╚══════════════════════════════════════════════╝
```

**If this project helped you, please drop a ⭐ — it genuinely means a lot.**

<br/>

[![GitHub Follow](https://img.shields.io/badge/Follow%20on-GitHub-181717?style=for-the-badge&logo=github&labelColor=0a0a0a)](https://github.com/ParthTyagi)
&nbsp;
[![Live Demo](https://img.shields.io/badge/Try%20the-Live%20Demo-d2494b?style=for-the-badge&labelColor=0a0a0a)](https://ai-fitness-api-68n1.onrender.com)

<br/>

</div>
