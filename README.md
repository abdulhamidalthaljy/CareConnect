# CareConnect

**Mobile Web Development - Final Project**  
**Johannes Kepler University Linz**  
**Winter Semester 2025/2026**

---

## Project Overview

CareConnect is a mobile-first Progressive Web Application (PWA) designed to bridge the communication gap between healthcare providers (doctors) and patients. It provides a unified platform for health management, appointment scheduling, and real-time communication.

### Live Demo

🌐 **Production URL:** https://careconnect-dj3i.onrender.com/

### Test Credentials

| Role    | Username   | Password   |
| ------- | ---------- | ---------- |
| Patient | Abdulhamid | Abdulhamid |
| Doctor  | admin1     | admin1     |

---

## Key Features

| Feature                       | Description                                                    |
| ----------------------------- | -------------------------------------------------------------- |
| **User Authentication**       | Secure registration, login, logout with password hashing       |
| **Role-Based Dashboards**     | Separate interfaces for patients and doctors                   |
| **Vitals Tracking**           | Record blood pressure, blood sugar with Chart.js visualization |
| **Medication Management**     | Add, view, delete medications                                  |
| **Real-Time Chat**            | Socket.IO powered instant messaging                            |
| **File Upload**               | Upload medical documents with image validation                 |
| **Appointment System**        | Book, confirm, cancel with status filtering                    |
| **Data Export**               | Download records as Excel (.xlsx) or PDF                       |
| **Doctor Patient Management** | Doctors can edit patient profiles, vitals, medicines           |

---

## Technology Stack

### Frontend

| Technology          | Purpose                           |
| ------------------- | --------------------------------- |
| HTML5               | Semantic markup                   |
| Tailwind CSS 2.2.19 | Utility-first responsive styling  |
| JavaScript ES6+     | Client interactivity, Fetch API   |
| Chart.js            | Data visualization                |
| Socket.IO Client    | Real-time WebSocket communication |

### Backend

| Technology     | Purpose                 |
| -------------- | ----------------------- |
| Python 3.11    | Server-side language    |
| Flask 2.2.2    | Web framework           |
| Flask-Login    | Session management      |
| Flask-SocketIO | WebSocket support       |
| Flask-WTF      | CSRF protection & forms |

### Database

| Technology        | Purpose             |
| ----------------- | ------------------- |
| SQLite            | Relational database |
| SQLAlchemy 1.4.27 | ORM                 |
| Flask-SQLAlchemy  | Flask integration   |

### Additional Libraries

| Library   | Purpose          |
| --------- | ---------------- |
| openpyxl  | Excel export     |
| ReportLab | PDF generation   |
| Pillow    | Image validation |
| Werkzeug  | Password hashing |

---

## Project Structure

```
CareConnect/
├── src/
│   ├── app.py              # Application factory & entry point
│   ├── config.py           # Configuration settings
│   ├── extensions.py       # Flask extensions (db, login, socketio, csrf)
│   ├── forms.py            # WTForms definitions
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py         # Database models (User, Vitals, Medicine, etc.)
│   ├── views/
│   │   ├── __init__.py
│   │   ├── main.py         # Main routes (dashboard, vitals, exports)
│   │   ├── auth.py         # Authentication routes
│   │   ├── doctor.py       # Doctor-specific routes
│   │   ├── appointments.py # Appointment management
│   │   └── chat.py         # Chat routes & Socket.IO events
│   ├── templates/
│   │   ├── layout.html     # Base template
│   │   ├── index.html      # Landing page
│   │   ├── dashboard.html  # Patient dashboard
│   │   ├── doctor_dashboard.html
│   │   ├── patient_view.html
│   │   ├── appointments.html
│   │   ├── chat.html
│   │   ├── auth/           # Login & register templates
│   │   └── components/     # Header & footer partials
│   └── static/
│       ├── css/
│       │   ├── tailwind.css  # Tailwind input
│       │   └── styles.css    # Compiled CSS
│       ├── js/
│       │   └── app.js        # Client-side JavaScript
│       ├── sw/
│       │   └── service-worker.js
│       └── icons/
│           └── webmanifest.json
├── tests/
│   ├── conftest.py         # pytest fixtures
│   ├── test_routes.py      # Route tests
│   └── test_exports_and_chat.py
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies (Tailwind)
├── tailwind.config.js      # Tailwind configuration
├── postcss.config.js       # PostCSS configuration
├── render.yaml             # Render deployment config
├── PRESENTATION_INFO.md    # Presentation details
└── README.md
```

---

## Database Schema

### Models (7 Tables)

```
User (id, username, email, password_hash, role)
  │
  ├── 1:1 ──► PatientProfile (full_name, address, health_history, allergies)
  ├── 1:N ──► Medicine (name, dosage)
  ├── 1:N ──► Vitals (type, value1, value2, timestamp)
  ├── 1:N ──► MedicalFile (original_filename, storage_filename)
  ├── N:M ──► Appointment (patient_id, doctor_id, start_time, status)
  └── N:M ──► ChatMessage (sender_id, receiver_id, message_text, timestamp)
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 16+ (for Tailwind CSS)

### Local Development

1. **Clone the repository:**

   ```bash
   git clone https://github.com/abdulhamidalthaljy/CareConnect.git
   cd CareConnect
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies & build CSS:**

   ```bash
   npm install
   npm run build
   ```

5. **Run the application:**

   ```bash
   python -m src.app
   ```

6. **Open browser:**
   ```
   http://127.0.0.1:5000
   ```

---

## API Endpoints

| Method    | Endpoint                      | Description               |
| --------- | ----------------------------- | ------------------------- |
| GET       | `/`                           | Landing page              |
| GET/POST  | `/login`                      | User authentication       |
| GET/POST  | `/register`                   | User registration         |
| GET       | `/logout`                     | End session               |
| GET       | `/dashboard`                  | Patient/Doctor dashboard  |
| POST      | `/add_vital`                  | Add vital record (JSON)   |
| GET       | `/api/get_vitals`             | Fetch vitals (JSON)       |
| POST      | `/upload_file`                | Upload medical file       |
| GET       | `/export_excel`               | Download Excel report     |
| GET       | `/export_pdf`                 | Download PDF report       |
| GET       | `/doctor`                     | Doctor dashboard          |
| GET       | `/doctor/view/<id>`           | View patient details      |
| POST      | `/doctor/update_profile/<id>` | Edit patient profile      |
| GET       | `/appointments`               | View appointments         |
| POST      | `/book_appointment`           | Create appointment        |
| GET       | `/chat/<id>`                  | Chat interface            |
| GET       | `/api/get_messages/<id>`      | Fetch chat history (JSON) |
| WebSocket | `private_message`             | Real-time chat event      |

---

## Deployment

The application is deployed on **Render.com** with automatic deployments from GitHub.

### Render Configuration (render.yaml)

```yaml
services:
  - type: web
    name: careconnect
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt && npm install && npm run build
    startCommand: gunicorn -k gevent -w 1 -b 0.0.0.0:$PORT "src.app:create_app()"
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: "3.11.0"
```

---

## Testing

Run the test suite:

```bash
pip install pytest pytest-flask
pytest -v
```

**Test Coverage:** 7 automated tests covering:

- Route accessibility
- User authentication
- Data export functionality
- Socket.IO messaging

---

## Mobile-First Design

- **Tailwind CSS** responsive utilities (`sm:`, `md:`, `lg:`)
- **Hamburger menu** for mobile navigation
- **Touch-friendly** buttons (44px minimum touch targets)
- **Responsive tables** with horizontal scroll
- **PWA features** (service worker, web manifest)

---

## Future Enhancements

- Push notifications for appointments
- Video consultations (WebRTC)
- AI-powered health insights
- Multi-language support
- Offline mode with service worker caching
- PostgreSQL for production database

---

## Author

**Abdulhamid Althaljy**  
Johannes Kepler University Linz  
Mobile Web Development - Winter Semester 2025/2026

---

## License

This project is submitted as part of academic coursework at JKU Linz.
