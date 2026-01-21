# CareConnect - Final Project Presentation Information

---

## 1. PROJECT OVERVIEW

### What is CareConnect?

CareConnect is a mobile-first Progressive Web Application (PWA) designed to bridge the communication gap between healthcare providers (doctors) and patients. It provides a unified platform for health management, appointment scheduling, and real-time communication.

### Problem Statement

- Patients struggle to track medical records, medications, and vitals
- Communication between patients and doctors is fragmented
- No centralized platform for healthcare data management
- Difficulty in scheduling and managing medical appointments

### Target Users

1. **Patients** - Track health data, communicate with doctors, manage appointments
2. **Doctors** - View patient records, manage appointments, provide remote consultations

### Key Features

| Feature                   | Description                                                    |
| ------------------------- | -------------------------------------------------------------- |
| User Authentication       | Secure registration, login, logout with password hashing       |
| Role-Based Dashboards     | Separate interfaces for patients and doctors                   |
| Vitals Tracking           | Record blood pressure, blood sugar with Chart.js visualization |
| Medication Management     | Add, view, delete medications                                  |
| Real-Time Chat            | Socket.IO powered instant messaging                            |
| File Upload               | Upload medical documents with Pillow image validation          |
| Appointment System        | Book, confirm, cancel with status filtering                    |
| Data Export               | Download records as Excel (.xlsx) or PDF                       |
| Doctor Patient Management | Doctors can edit patient profiles, vitals, medicines           |

### Live Demo URL

- **Production:** https://careconnect-iphc.onrender.com/
- **GitHub Repository:** https://github.com/abdulhamidalthaljy/CareConnect

### Test Credentials

- **Patient Account:** Username: `Abdulhamid` / Password: `Abdulhamid`
- **Doctor Account:** Username: `admin1` / Password: `admin1`

---

## 2. DEVELOPMENT PROCESS

### Development Timeline

| Phase                      | Activities                                                           |
| -------------------------- | -------------------------------------------------------------------- |
| **Planning**               | Requirements gathering, feature prioritization, tech stack selection |
| **Setup**                  | Flask project structure, virtual environment, Git repository         |
| **Core Development**       | Authentication, database models, basic routes                        |
| **Feature Implementation** | Vitals tracking, medicines, appointments, file uploads               |
| **Real-Time Features**     | Socket.IO chat integration                                           |
| **UI/UX**                  | Tailwind CSS styling, responsive design, mobile optimization         |
| **Testing**                | pytest test suite (7 automated tests)                                |
| **Deployment**             | Render.com cloud deployment with CI/CD                               |
| **Bug Fixes**              | Role normalization, CSRF protection, export permissions              |

### Version Control (Git/GitHub)

- Repository: https://github.com/abdulhamidalthaljy/CareConnect
- Branch strategy: Single `main` branch with feature commits
- Commit history shows iterative development
- `.gitignore` configured for Python/Node artifacts

### Deployment (Render.com)

- **Platform:** Render.com (Free Tier)
- **Auto-Deploy:** Connected to GitHub - pushes trigger automatic deployment
- **Build Process:**
  1. `pip install -r requirements.txt` - Install Python dependencies
  2. `npm install` - Install Node.js dependencies
  3. `npm run build` - Compile Tailwind CSS
- **Runtime:** Gunicorn WSGI server with Gevent async workers
- **Environment Variables:** SECRET_KEY (auto-generated), PYTHON_VERSION=3.11.0

### Development Tools Used

| Tool            | Purpose                      |
| --------------- | ---------------------------- |
| VS Code         | Primary IDE                  |
| Git             | Version control              |
| GitHub          | Remote repository hosting    |
| Render.com      | Cloud deployment platform    |
| Chrome DevTools | Debugging, Lighthouse audits |
| pytest          | Automated testing            |

---

## 3. TECHNICAL CHALLENGES FACED

### Challenge 1: Role-Based Access Control Issues

- **Problem:** Doctors getting 403 Forbidden errors when accessing patient data
- **Root Cause:** Case-sensitive role comparisons (`"Doctor"` vs `"doctor"`)
- **Impact:** Doctors couldn't view appointments or patient information

### Challenge 2: Real-Time Chat Deployment

- **Problem:** Socket.IO not working in production with eventlet
- **Root Cause:** Eventlet monkey_patch warnings and compatibility issues with Gunicorn
- **Impact:** Chat feature failing on Render deployment

### Challenge 3: CSRF Token Issues

- **Problem:** "Add Vital" button returning 400 Bad Request
- **Root Cause:** JavaScript fetch requests missing CSRF token headers
- **Impact:** Patients couldn't add vitals from dashboard

### Challenge 4: Export Permissions

- **Problem:** Doctors getting 403 when exporting patient PDF/Excel
- **Root Cause:** Export routes required appointment association
- **Impact:** Doctors couldn't download patient records

### Challenge 5: Deployment Configuration

- **Problem:** Render build failing with "requirements.txt not found"
- **Root Cause:** Root Directory incorrectly set to `src/` instead of repository root
- **Impact:** Deployment failures

### Challenge 6: Mobile Responsiveness

- **Problem:** UI elements not scaling properly on mobile devices
- **Root Cause:** Fixed-width layouts and non-responsive components
- **Impact:** Poor mobile user experience

---

## 4. SOLUTIONS IMPLEMENTED

### Solution 1: Role Normalization

```python
# Before (case-sensitive)
if current_user.role == 'doctor':

# After (case-insensitive)
if (current_user.role or '').strip().lower() == 'doctor':
```

- Applied across all views: `main.py`, `doctor.py`, `appointments.py`, `auth.py`
- Normalized role storage on registration to lowercase
- Used `ilike` for case-insensitive database queries

### Solution 2: Switched from Eventlet to Gevent

```python
# src/extensions.py
try:
    import gevent
    _async_mode = 'gevent'
except ImportError:
    _async_mode = 'threading'

socketio = SocketIO(async_mode=_async_mode, cors_allowed_origins='*')
```

- Changed Gunicorn worker from `eventlet` to `gevent`
- Updated `requirements.txt`: replaced eventlet with gevent + gevent-websocket
- Updated `render.yaml` start command: `gunicorn -k gevent -w 1 ...`

### Solution 3: CSRF Token in JavaScript

```javascript
// Read CSRF token from meta tag
window.__CARECONNECT_CSRF_TOKEN = document
  .querySelector('meta[name="csrf-token"]')
  ?.getAttribute("content");

// Include in fetch headers
fetch("/add_vital", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": window.__CARECONNECT_CSRF_TOKEN,
  },
  body: JSON.stringify(payload),
});
```

### Solution 4: Relaxed Export Permissions

```python
# Before: Required appointment association
assoc = Appointment.query.filter_by(doctor_id=current_user.id, patient_id=pid).first()
if not assoc:
    abort(403)

# After: Just verify patient exists
patient = User.query.get(pid)
if not patient or (patient.role or '').strip().lower() != 'patient':
    abort(404)
```

### Solution 5: Correct Render Configuration

- Cleared Root Directory setting (was incorrectly set to `src/`)
- Set PYTHON_VERSION environment variable to `3.11.0`
- Configured proper build and start commands

### Solution 6: Tailwind CSS Mobile-First Design

- Used Tailwind's responsive prefixes: `sm:`, `md:`, `lg:`
- Implemented mobile navigation with hamburger menu
- Used `flex`, `grid` for responsive layouts
- Applied `min-h-screen`, `w-full` for full mobile coverage

---

## 5. SYSTEM ARCHITECTURE

### Overall Client-Server Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                          │
├─────────────────────────────────────────────────────────────────┤
│  Mobile Browser / Desktop Browser                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   HTML5     │  │ Tailwind CSS│  │     JavaScript          │  │
│  │  (Jinja2)   │  │ (Responsive)│  │ (Fetch API, Socket.IO)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP / WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVER (Flask Backend)                       │
├─────────────────────────────────────────────────────────────────┤
│  Gunicorn WSGI Server (Gevent Workers)                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Flask Application                         ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    ││
│  │  │  Views   │  │  Models  │  │Templates │  │  Static  │    ││
│  │  │(Blueprints)│ │(SQLAlchemy)│ │ (Jinja2) │  │(CSS/JS)  │    ││
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    ││
│  │  ┌──────────────────────────────────────────────────────┐  ││
│  │  │              Flask Extensions                         │  ││
│  │  │  Flask-Login │ Flask-SocketIO │ Flask-WTF │ Flask-SQL │  ││
│  │  └──────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (SQLite)                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │  Users  │ │ Profiles│ │Medicines│ │ Vitals  │ │Appointments│ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────────┘ │
│  ┌─────────────┐ ┌─────────────┐                                │
│  │ChatMessages │ │MedicalFiles │                                │
│  └─────────────┘ └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

### Routing Strategy (Flask Blueprints)

```
CareConnect/
├── src/
│   ├── app.py              # Application factory, blueprint registration
│   ├── views/
│   │   ├── main.py         # Blueprint: main (/, /dashboard, /add_vital, /export_*)
│   │   ├── auth.py         # Blueprint: auth (/login, /register, /logout)
│   │   ├── doctor.py       # Blueprint: doctor (/doctor, /doctor/view/<id>)
│   │   ├── appointments.py # Blueprint: appointments (/appointments, /book)
│   │   └── chat.py         # Blueprint: chat + Socket.IO events
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── layout.html     # Base template with navigation
│   │   ├── dashboard.html  # Patient dashboard
│   │   ├── doctor_dashboard.html
│   │   ├── patient_view.html
│   │   ├── auth/login.html, register.html
│   │   └── components/header.html, footer.html
│   └── static/
│       ├── css/styles.css  # Compiled Tailwind CSS
│       └── js/app.js       # Client-side JavaScript
```

### API Endpoints Summary

| Method    | Endpoint                      | Purpose                  |
| --------- | ----------------------------- | ------------------------ |
| GET       | `/`                           | Landing page             |
| GET       | `/dashboard`                  | Patient/Doctor dashboard |
| POST      | `/login`                      | User authentication      |
| POST      | `/register`                   | User registration        |
| GET       | `/logout`                     | End session              |
| POST      | `/add_vital`                  | Add vital record (JSON)  |
| GET       | `/api/get_vitals`             | Fetch vitals (JSON)      |
| POST      | `/upload_file`                | Upload medical file      |
| GET       | `/export_excel`               | Download Excel report    |
| GET       | `/export_pdf`                 | Download PDF report      |
| GET       | `/doctor`                     | Doctor dashboard         |
| GET       | `/doctor/view/<id>`           | View patient details     |
| POST      | `/doctor/update_profile/<id>` | Edit patient profile     |
| GET       | `/appointments`               | View appointments        |
| POST      | `/book_appointment`           | Create appointment       |
| GET       | `/api/get_messages/<id>`      | Fetch chat history       |
| WebSocket | `private_message`             | Real-time chat           |

---

## 6. FRONTEND INTERACTION & STATE HANDLING

### JavaScript Dynamic Updates

#### Fetch API for AJAX Requests

```javascript
// Loading vitals data
function loadVitals() {
  fetch("/api/get_vitals")
    .then((res) => res.json())
    .then((data) => {
      renderVitalsTable(data);
      renderVitalsChart(data);
    })
    .catch((err) => console.error("Error loading vitals:", err));
}

// Adding a vital with CSRF protection
function addVital() {
  const payload = { type: type, value1: value1, value2: value2 };
  fetch("/add_vital", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": window.__CARECONNECT_CSRF_TOKEN,
    },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then((resp) => {
      if (resp.status === "ok") {
        loadVitals(); // Refresh data
        showVitalMessage("Vital added.", "success");
      }
    });
}
```

#### WebSocket (Socket.IO) for Real-Time Chat

```javascript
// Connect to Socket.IO
const socket = io();

// Listen for incoming messages
socket.on("private_message", function (data) {
  appendMessage(data.sender, data.message, "received");
});

// Send message
function sendMessage() {
  socket.emit("private_message", {
    receiver_id: receiverId,
    message: messageText,
  });
}
```

#### Chart.js for Data Visualization

```javascript
// Render vitals chart with multiple datasets
function renderVitalsChart(data) {
  const ctx = document.getElementById("vitalsChart");
  vitalsChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map((v) => new Date(v.timestamp).toLocaleString()),
      datasets: [
        {
          label: "Systolic (BP)",
          data: systolicValues,
          borderColor: "rgba(220,38,38,1)",
        },
        {
          label: "Diastolic (BP)",
          data: diastolicValues,
          borderColor: "rgba(34,197,94,1)",
        },
        {
          label: "Blood Sugar",
          data: sugarValues,
          borderColor: "rgba(59,130,246,1)",
        },
      ],
    },
    options: { responsive: true },
  });
}
```

### Form Validation & UI Feedback

#### Client-Side Validation

```javascript
function addVital() {
  const value1 = document.getElementById("vital-value1").value;

  // Client-side validation before server request
  if (!value1 || isNaN(parseFloat(value1))) {
    showVitalMessage("Value 1 is required and must be a number.", "danger");
    return;
  }
  // ... proceed with fetch
}
```

#### Server-Side Validation (Flask-WTF)

```python
# Registration form with WTForms validation
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')])
```

#### UI Feedback Messages

```javascript
function showVitalMessage(msg, category) {
  const area = document.getElementById("vital-message");
  const div = document.createElement("div");
  div.className =
    "p-2 rounded " +
    (category === "success"
      ? "bg-green-100 text-green-800"
      : "bg-red-100 text-red-800");
  div.textContent = msg;
  area.appendChild(div);
  setTimeout(() => {
    area.innerHTML = "";
  }, 4000); // Auto-dismiss
}
```

---

## 7. BACKEND DESIGN & DATA MODEL

### Database Models (7 Tables)

#### Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ password_hash   │
│ role            │
└────────┬────────┘
         │
         │ 1:1
         ▼
┌─────────────────┐
│ PatientProfile  │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │──────► User
│ full_name       │
│ address         │
│ health_history  │
│ allergies       │
└─────────────────┘

User ◄──── 1:N ────► Medicine
User ◄──── 1:N ────► Vitals
User ◄──── 1:N ────► MedicalFile
User ◄──── N:M ────► Appointment (patient_id, doctor_id)
User ◄──── N:M ────► ChatMessage (sender_id, receiver_id)
```

#### SQLAlchemy Model Definitions

```python
# User Model (One-to-Many relationships)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(200))
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='patient')

    # Relationships (One-to-Many)
    profile = db.relationship('PatientProfile', back_populates='user', uselist=False)
    medicines = db.relationship('Medicine', back_populates='patient', cascade='all, delete-orphan')
    vitals = db.relationship('Vitals', back_populates='patient', cascade='all, delete-orphan')
    files = db.relationship('MedicalFile', back_populates='patient', cascade='all, delete-orphan')

# Appointment Model (Many-to-Many through foreign keys)
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending/confirmed/cancelled

# ChatMessage Model (Self-referential Many-to-Many)
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

### Relationship Types

| Relationship          | Type         | Description                                      |
| --------------------- | ------------ | ------------------------------------------------ |
| User → PatientProfile | One-to-One   | Each patient has one profile                     |
| User → Medicine       | One-to-Many  | Patient can have multiple medications            |
| User → Vitals         | One-to-Many  | Patient can have multiple vital records          |
| User → MedicalFile    | One-to-Many  | Patient can upload multiple files                |
| User ↔ Appointment    | Many-to-Many | Patients and doctors linked through appointments |
| User ↔ ChatMessage    | Many-to-Many | Users can message each other                     |

### Database Constraints

- Primary keys on all tables (`id`)
- Foreign key constraints with `db.ForeignKey()`
- Unique constraint on `username`
- Not-null constraints on required fields
- Cascade delete on child records (`cascade='all, delete-orphan'`)

---

## 8. MOBILE-FIRST & RESPONSIVE DESIGN

### Tailwind CSS Responsive Techniques

#### Mobile-First Breakpoints

```html
<!-- Mobile-first: base styles apply to mobile, then scale up -->
<div class="w-full md:w-1/2 lg:w-1/3">
  <!-- Full width on mobile, half on medium, third on large -->
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- 1 column mobile, 2 columns tablet, 3 columns desktop -->
</div>
```

#### Mobile Navigation (Hamburger Menu)

```html
<!-- Mobile menu button (visible on small screens) -->
<button id="mobile-menu-btn" class="md:hidden p-2">
  <svg class="w-6 h-6"><!-- hamburger icon --></svg>
</button>

<!-- Mobile menu (hidden by default, toggled via JS) -->
<div id="mobile-menu" class="hidden md:hidden">
  <a href="/dashboard" class="block px-4 py-2">Dashboard</a>
  <a href="/appointments" class="block px-4 py-2">Appointments</a>
</div>

<!-- Desktop menu (hidden on mobile) -->
<nav class="hidden md:flex space-x-4">
  <a href="/dashboard">Dashboard</a>
  <a href="/appointments">Appointments</a>
</nav>
```

```javascript
// Toggle mobile menu
document
  .getElementById("mobile-menu-btn")
  .addEventListener("click", function () {
    document.getElementById("mobile-menu").classList.toggle("hidden");
  });
```

#### Responsive Forms

```html
<form class="space-y-4 max-w-md mx-auto p-4">
  <input
    type="text"
    class="w-full p-3 border rounded-lg text-base"
    placeholder="Username"
  />
  <!-- text-base ensures 16px font (prevents iOS zoom) -->

  <button
    class="w-full py-3 bg-blue-600 text-white rounded-lg 
                   active:bg-blue-700 touch-manipulation"
  >
    <!-- touch-manipulation improves touch response -->
    Login
  </button>
</form>
```

#### Responsive Tables

```html
<!-- Scrollable table on mobile -->
<div class="overflow-x-auto">
  <table class="min-w-full">
    <thead>
      <tr>
        <th class="px-2 py-1 text-sm md:px-4 md:py-2 md:text-base">Type</th>
        <th class="px-2 py-1 text-sm md:px-4 md:py-2 md:text-base">Value</th>
      </tr>
    </thead>
  </table>
</div>
```

### Touch Interactions

```css
/* Larger touch targets for mobile */
.btn-touch {
  min-height: 44px; /* Apple's recommended minimum */
  min-width: 44px;
  padding: 12px 24px;
}

/* Prevent text selection on buttons */
button {
  -webkit-user-select: none;
  user-select: none;
}
```

### Performance Optimizations

- **Minimal CSS:** Tailwind purges unused styles in production
- **Lazy loading:** Charts load after page render
- **Compressed images:** Pillow validates and can resize uploads
- **Async requests:** Fetch API doesn't block UI

---

## 9. LIGHTHOUSE PERFORMANCE & MOBILE OPTIMIZATION

### How to Generate Lighthouse Report

1. Open Chrome DevTools (F12)
2. Go to **Lighthouse** tab
3. Select **Mobile** device
4. Check: Performance, Accessibility, Best Practices, SEO
5. Click **Analyze page load**

### Expected Lighthouse Metrics

| Category           | Target | Techniques Used                                                  |
| ------------------ | ------ | ---------------------------------------------------------------- |
| **Performance**    | 70+    | Minimal CSS (Tailwind purge), async JS loading, optimized images |
| **Accessibility**  | 80+    | Semantic HTML, ARIA labels, color contrast, form labels          |
| **Best Practices** | 80+    | HTTPS, no console errors, secure headers                         |
| **SEO**            | 80+    | Meta tags, responsive design, semantic markup                    |

### Optimizations Implemented

#### Performance

- Tailwind CSS purges unused styles (~10KB final CSS)
- JavaScript deferred loading
- Chart.js loaded from CDN with caching
- No render-blocking resources

#### Accessibility

```html
<!-- Semantic HTML -->
<main role="main">
  <h1>Dashboard</h1>
  <nav aria-label="Main navigation">
    <!-- Form labels -->
    <label for="vital-type">Vital Type</label>
    <select id="vital-type" name="type">
      <!-- Button labels -->
      <button aria-label="Open menu"></button>
    </select>
  </nav>
</main>
```

#### PWA Features

```html
<!-- Web manifest for installability -->
<link rel="manifest" href="/static/icons/webmanifest.json" />

<!-- Theme color for mobile browsers -->
<meta name="theme-color" content="#2563eb" />
```

```json
// webmanifest.json
{
  "name": "CareConnect",
  "short_name": "CareConnect",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#2563eb",
  "background_color": "#ffffff"
}
```

---

## 10. TECHNOLOGY STACK SUMMARY

### Frontend

| Technology       | Version | Purpose                          |
| ---------------- | ------- | -------------------------------- |
| HTML5            | -       | Semantic markup                  |
| Tailwind CSS     | 2.2.19  | Utility-first responsive styling |
| JavaScript ES6+  | -       | Client interactivity             |
| Chart.js         | CDN     | Data visualization               |
| Socket.IO Client | 4.x     | Real-time WebSocket              |

### Backend

| Technology     | Version | Purpose              |
| -------------- | ------- | -------------------- |
| Python         | 3.11    | Server-side language |
| Flask          | 2.2.2   | Web framework        |
| Flask-Login    | 0.6.2   | Session management   |
| Flask-SocketIO | 5.3.0   | WebSocket support    |
| Flask-WTF      | 1.0.0   | CSRF & forms         |
| Gunicorn       | 23.0    | WSGI server          |
| Gevent         | 25.x    | Async workers        |

### Database

| Technology       | Version | Purpose             |
| ---------------- | ------- | ------------------- |
| SQLite           | 3.x     | Relational database |
| SQLAlchemy       | 1.4.27  | ORM                 |
| Flask-SQLAlchemy | 3.0.3   | Flask integration   |

### Additional Libraries

| Library   | Purpose          |
| --------- | ---------------- |
| openpyxl  | Excel export     |
| ReportLab | PDF generation   |
| Pillow    | Image validation |
| Werkzeug  | Password hashing |

### DevOps

| Tool       | Purpose              |
| ---------- | -------------------- |
| Git/GitHub | Version control      |
| Render.com | Cloud hosting (PaaS) |
| pytest     | Automated testing    |

---

## 11. FUTURE ENHANCEMENTS

| Enhancement                 | Description                                          |
| --------------------------- | ---------------------------------------------------- |
| **Push Notifications**      | Alert patients of appointments, medication reminders |
| **Video Consultations**     | WebRTC integration for telemedicine                  |
| **AI Health Insights**      | ML-based analysis of vitals trends                   |
| **Multi-language Support**  | i18n for broader accessibility                       |
| **Prescription Management** | Digital prescriptions with pharmacy integration      |
| **Calendar Sync**           | Google/Outlook calendar integration                  |
| **Offline Support**         | Service worker caching for offline access            |
| **PostgreSQL Migration**    | Production-grade database                            |

---

## 12. DEMO FLOW (15 minutes)

### Slides (7 minutes)

1. **Slide 1:** Project Overview & Objectives (1 min)
2. **Slide 2:** System Architecture Diagram (1 min)
3. **Slide 3:** Technology Stack (1 min)
4. **Slide 4:** Database Schema (1 min)
5. **Slide 5:** Technical Challenges & Solutions (1.5 min)
6. **Slide 6:** Mobile-First Design & Lighthouse (1 min)
7. **Slide 7:** Future Enhancements (0.5 min)

### Live Demo (8 minutes)

1. **Landing Page** - Show responsive design (0.5 min)
2. **Patient Login** - Login as Abdulhamid (0.5 min)
3. **Patient Dashboard** - Show vitals chart, add a vital (1.5 min)
4. **Medications** - Add a medication (0.5 min)
5. **File Upload** - Upload a document (0.5 min)
6. **Export** - Download PDF/Excel (0.5 min)
7. **Logout & Doctor Login** - Login as admin1 (0.5 min)
8. **Doctor Dashboard** - Show patient list (0.5 min)
9. **Patient View** - Edit patient profile, add vital (1 min)
10. **Appointments** - Show filtering (0.5 min)
11. **Chat** - Send a message (1 min)
12. **Lighthouse Report** - Show mobile audit (0.5 min)

---

## 13. PROJECT STRUCTURE

```
CareConnect/
├── src/
│   ├── app.py                # Main entry point, application factory
│   ├── config.py             # Configuration settings
│   ├── extensions.py         # Flask extensions (db, login, socketio, csrf)
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py           # All 7 database models
│   ├── views/
│   │   ├── __init__.py
│   │   ├── main.py           # Main routes (dashboard, vitals, exports)
│   │   ├── auth.py           # Authentication routes
│   │   ├── doctor.py         # Doctor-specific routes
│   │   ├── appointments.py   # Appointment management
│   │   └── chat.py           # Chat routes and Socket.IO events
│   ├── templates/
│   │   ├── layout.html       # Base template
│   │   ├── index.html        # Landing page
│   │   ├── dashboard.html    # Patient dashboard
│   │   ├── doctor_dashboard.html
│   │   ├── patient_view.html # Doctor's view of patient
│   │   ├── appointments.html
│   │   ├── chat.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── components/
│   │       ├── header.html
│   │       └── footer.html
│   └── static/
│       ├── css/
│       │   ├── tailwind.css  # Tailwind input
│       │   └── styles.css    # Compiled output
│       ├── js/
│       │   └── app.js        # Client-side JavaScript
│       └── icons/
│           └── webmanifest.json
├── tests/
│   ├── conftest.py           # pytest fixtures
│   ├── test_routes.py        # Route tests
│   └── test_exports_and_chat.py
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies (Tailwind)
├── tailwind.config.js        # Tailwind configuration
├── render.yaml               # Render deployment config
├── README.md
└── .gitignore
```

---

## 14. REQUIREMENTS FILES

### requirements.txt (Python)

```
Flask==2.2.2
Flask-Login==0.6.2
Flask-SocketIO==5.3.0
Flask-WTF==1.0.0
SQLAlchemy==1.4.27
Werkzeug==2.2.2
python-dotenv==0.19.2
Flask-SQLAlchemy
openpyxl
reportlab
Pillow
gunicorn
gevent
gevent-websocket
```

### package.json (Node.js)

```json
{
  "name": "CareConnect",
  "version": "1.0.0",
  "scripts": {
    "build": "tailwindcss build src/static/css/tailwind.css -o src/static/css/styles.css",
    "watch": "tailwindcss -i src/static/css/tailwind.css -o src/static/css/styles.css --watch"
  },
  "dependencies": {
    "tailwindcss": "^2.2.19",
    "postcss": "^8.4.6",
    "autoprefixer": "^10.4.2"
  }
}
```

---

## 15. RENDER DEPLOYMENT CONFIGURATION

### render.yaml

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

### Environment Variables on Render

| Variable       | Value          | Purpose                |
| -------------- | -------------- | ---------------------- |
| SECRET_KEY     | Auto-generated | Flask session security |
| PYTHON_VERSION | 3.11.0         | Specify Python version |

---

_This document contains all the information needed to generate presentation slides for the CareConnect final project._
