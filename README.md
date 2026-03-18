<div align="center">

<img src="https://img.shields.io/badge/⬡-AI--DFIS-00ffcc?style=for-the-badge&labelColor=0a0a0a&color=00ffcc" alt="AI-DFIS"/>

# AI Driven Fitness Intelligence System

### *Your Body. Decoded.*

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-AI--DFIS-00ffcc?style=for-the-badge&labelColor=111)](https://ai-fitness-api-68n1.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Machine Learning](https://img.shields.io/badge/ML-Powered-ff6b35?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![GitHub Stars](https://img.shields.io/github/stars/ParthTyagi?style=for-the-badge&color=gold)](https://github.com)

> A full-stack, machine learning–powered fitness intelligence platform that analyses 12+ biometric data points to deliver real-time body fat predictions, personalised training splits, and goal-aligned recommendations — all wrapped in a sleek, futuristic UI.

</div>

---

## 📸 Screenshots

> **👉 How to add your screenshots:**
> 1. Take screenshots of each page (Login, Register, Dashboard, Prediction, History)
> 2. Place them inside a folder called `assets/screenshots/` in your repo
> 3. They will automatically appear below

<div align="center">

### 🔐 Login — Secure Access Terminal
<!-- Replace the path below with your actual screenshot -->
![Login Page](assets/screenshots/login.png)

### 📝 Register — Deploy Your Profile
![Register Page](assets/screenshots/register.png)

### 📊 Dashboard — Intelligence Overview
![Dashboard](assets/screenshots/dashboard.png)

### 🧬 Body Fat Prediction — ML Engine
![Prediction](assets/screenshots/prediction.png)

### 📈 Prediction History — Track Your Progress
![History](assets/screenshots/history.png)

</div>

---

## ✨ Features

| Module | Feature | Status |
|--------|---------|--------|
| ⚡ **ML Prediction** | Real-time body fat % prediction using trained ML model | ✅ Live |
| 🧬 **Biometric Analysis** | 12+ data points: age, weight, height, BMI, skinfolds & more | ✅ Live |
| 📊 **History Tracking** | Full prediction history logged per user | ✅ Live |
| 🎯 **Workout Splits** | Custom weekly training splits aligned to your goals | ✅ Live |
| 🔐 **Auth System** | Secure login, registration & password recovery | ✅ Live |
| 📱 **Responsive UI** | Futuristic, mobile-friendly interface | ✅ Live |

---

## 🧠 How It Works

```
User Input (12+ Biometrics)
        │
        ▼
  ┌─────────────┐
  │  Flask API  │  ← Handles auth, routing, and data flow
  └──────┬──────┘
         │
         ▼
  ┌─────────────────────┐
  │   ML Prediction     │  ← Trained regression / classification model
  │   Engine            │     predicts body fat percentage
  └──────┬──────────────┘
         │
         ▼
  ┌──────────────────────────────┐
  │  Personalised Recommendations │  ← Training splits + goal-based advice
  └──────────────────────────────┘
         │
         ▼
    Dashboard & History
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Jinja2 Templates |
| **Backend** | Python, Flask |
| **ML / Data** | Scikit-learn, Pandas, NumPy |
| **Database** | SQLite / SQLAlchemy |
| **Auth** | Flask-Login, Werkzeug |
| **Hosting** | Render |

</div>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-fitness-api.git
cd ai-fitness-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Then open your browser at `http://localhost:5000` 🎉

---

## 📂 Project Structure

```
ai-fitness-api/
│
├── app.py                  # Main Flask application
├── models/
│   ├── user.py             # User model & auth
│   └── prediction.py       # Prediction history model
├── ml/
│   └── model.pkl           # Trained ML model
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── prediction.html
├── static/
│   └── css / js / assets
├── requirements.txt
└── README.md
```

> *(Update this tree to match your actual structure)*

---

## 🧬 Biometric Inputs Analysed

The ML engine processes the following data points to generate predictions:

- **Age** · **Gender** · **Height** · **Weight**
- **BMI** · **Waist Circumference** · **Hip Circumference**
- **Neck Circumference** · **Chest Skinfold** · **Abdomen Skinfold**
- **Thigh Skinfold** · **Activity Level**

---

## 🗺️ Roadmap

- [x] ML body fat prediction engine
- [x] User authentication (login / register / reset)
- [x] Prediction history tracking
- [x] Custom workout split generation
- [ ] Progress visualisation charts
- [ ] Mobile app (React Native / Flutter)
- [ ] Nutrition recommendations
- [ ] Wearable device integration (Fitbit, Apple Watch)
- [ ] API documentation (Swagger / Postman)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Developed with 💪 by [Parth Tyagi](https://github.com/ParthTyagi)**

*If you found this useful, please consider giving it a ⭐ — it means a lot!*

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/ParthTyagi)

</div>
