## 🌐 Live Demo

🚀 The Tractent application is live and deployed on Render:

👉 **Live Website:** https://tractent-website.onrender.com/

> Note: The application may take a few seconds to load initially because Render free services sleep after inactivity.
# 🚜 Tractent — Smart Tractor Rental Platform

> Connecting farmers with tractor providers through a seamless digital experience.

Tractent is a smart tractor rental platform that enables farmers (customers) to search, book, and track tractors based on location, while providing providers with an easy way to manage their fleet and bookings — all secured through robust authentication and a microservices-inspired architecture.

---

## 🎯 Problem Statement

Farmers often face difficulties in:

- Finding tractors available nearby
- Comparing prices and models
- Verifying service availability
- Managing bookings efficiently

**Tractent** solves these challenges by providing a centralized digital platform for tractor rentals.

---

## ✨ Features

### 👤 User Features
- User Signup & Login Authentication
- Search tractors by location
- Filter tractors by Model & Price
- Book tractors online
- View booking history

### 🚜 Provider Features
- Add tractors to the platform
- Manage tractor availability
- View and manage booking requests

### 📍 Smart Location System
- Location validation during booking
- Tractor recommendations based on user location
- Search-based filtering

### 🧑‍💼 Mediator / Delivery System
- Company staff assigned to deliver tractors
- Live location tracking during delivery

---

## 🏗️ System Architecture

The project follows a **Microservices-Based Design (Logical Microservices)** where each functionality behaves as an independent service module.

```
                ┌──────────────┐
                │   Frontend   │
                │ (HTML/CSS)   │
                └──────┬───────┘
                       │
                Flask API Gateway
                       │
 ┌────────────┬──────────────┬──────────────┬──────────────┐
 │Auth Service│Booking Service│Location Service│Recommendation│
 │            │               │               │   Service     │
 └────────────┴──────────────┴──────────────┴──────────────┘
                       │
                     Database
                    (MongoDB Atlas)
```

---

## ⚙️ Microservices Overview

Although deployed as a single Flask application, Tractent follows microservice principles by separating responsibilities into independent service layers.

### 1️⃣ Authentication Service
| Detail | Info |
|---|---|
| **Responsibility** | User registration, login validation, password hashing, session management |
| **Modules** | Flask, Passlib (bcrypt), Session handling |
| **Endpoints** | `POST /signup`, `POST /login`, `GET /logout` |

### 2️⃣ Booking Service
| Detail | Info |
|---|---|
| **Responsibility** | Tractor booking, validation, and booking history |
| **Key Logic** | Checks availability, stores details, links customer & provider |
| **Endpoints** | `POST /book_tractor`, `GET /history` |

### 3️⃣ Location Service
| Detail | Info |
|---|---|
| **Responsibility** | Validate user location and match tractors by region |
| **How It Works** | Accepts user location → Filters tractors → Ensures provider coverage |
| **Endpoints** | `GET /search?location=` |

### 4️⃣ Recommendation Service
| Detail | Info |
|---|---|
| **Responsibility** | Recommend tractors dynamically with filters (price, model) |
| **Logic** | Location-based filtering and query optimization |

### 5️⃣ Mediator / Delivery Service
| Detail | Info |
|---|---|
| **Responsibility** | Assign staff mediators, track delivery, update booking status |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | MongoDB Atlas |
| ODM | PyMongo / MongoEngine |
| Authentication | Passlib (bcrypt) |
| Frontend | HTML, CSS, Jinja2 |
| Containerization | Docker |
| Deployment | Render |
| Version Control | Git & GitHub |

---

## 📂 Project Structure

```
Tractent/
│
├── app.py               # Main Flask application & API gateway
├── models.py            # Database models
├── database.py          # Database connection setup
├── migration.py         # Database setup / migrations
├── templates/           # Jinja2 HTML templates
├── static/              # CSS, JS, and assets
│   └── js/
├── frontend/            # Frontend source files
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
└── README.md
```

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Tarutiwari/Tractent_website.git
cd Tractent_website
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?appName=Cluster0
SECRET_KEY=your_secret_key
```

> **Note:** Replace `<username>` and `<password>` with your MongoDB Atlas credentials. Never commit your `.env` file to Git.

### 5️⃣ Run the Application
```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t tractent .

# Run the container (pass your MongoDB URI as an env variable)
docker run -p 5000:10000 -e MONGO_URI="your_mongo_uri" -e SECRET_KEY="your_secret" tractent
```

---

## ☁️ Deployment on Render

1. Connect your GitHub repository to [Render](https://render.com)
2. Add the required environment variables (`MONGO_URI`, `SECRET_KEY`)
3. Deploy as a **Web Service**

---

## 🔐 Security Features

- ✅ Password hashing using **bcrypt**
- ✅ Session-based authentication
- ✅ Protected routes (login required)
- ✅ Input validation on all endpoints

---

## 📈 Future Enhancements

- [ ] Real-time GPS tracking
- [ ] Payment gateway integration
- [ ] AI-based tractor recommendation engine
- [ ] Mobile application (iOS & Android)
- [ ] Push notification system

---

## 👩‍💻 Author

**Taru Tiwari** — Computer Science Engineer

- 🐙 GitHub: [@Tarutiwari](https://github.com/Tarutiwari)
- 💼 LinkedIn: [Taru Tiwari](https://www.linkedin.com/in/taru-tiwari-0b7b5b250)

---

## 📄 License

This project is developed for **educational and learning purposes**.

---

<p align="center">Made by Taru Tiwari</p>
