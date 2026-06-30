import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, render_template_string, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-community-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///community_v3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please sign in to access this page."
login_manager.login_message_category = "info"

# CATEGORY CONFIG MATRIX
CATEGORIES = [
    "Medical Assistance",
    "Food & Groceries",
    "Technical Support",
    "Disaster Response",
    "General Labor"
]

# ==========================================
# DATABASE MODELS
# ==========================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class HelpRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(150), nullable=False, default="Anonymous User")
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False, default="General Labor")
    description = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False, default="General Labor")
    skills = db.Column(db.String(300), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))

# ==========================================
# MODERN CYBER ANIMATED UI & TEMPLATES
# ==========================================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community Help Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #060913;
            --bg-card: #0d1527;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --accent-glow: #0ea5e9;
            --accent-purple: #a855f7;
            --accent-success: #10b981;
            --border-color: #1e2943;
        }
        
        body { 
            background-color: var(--bg-main); 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            color: var(--text-main);
            overflow-x: hidden;
            position: relative;
        }
        
        body::before {
            content: "";
            position: fixed;
            top: -50%; left: -50%; right: -50%; bottom: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 15% 20%, rgba(14, 165, 233, 0.12) 0%, transparent 40%),
                        radial-gradient(circle at 85% 70%, rgba(168, 85, 247, 0.1) 0%, transparent 45%);
            animation: driftBackground 25s ease-in-out infinite alternate;
            z-index: -1;
        }
        @keyframes driftBackground {
            0% { transform: translate(0, 0) rotate(0deg); }
            50% { transform: translate(-2%, 3%) rotate(2deg); }
            100% { transform: translate(1%, -1%) rotate(-1deg); }
        }
        
        .navbar { 
            background-color: rgba(6, 9, 19, 0.75) !important; 
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-color);
        }
        .navbar-brand { 
            font-weight: 800; 
            background: linear-gradient(to right, var(--accent-glow), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .hero-section { 
            padding: 60px 0 50px 0; 
            text-align: center;
        }
        
        .card { 
            background-color: var(--bg-card);
            border: 1px solid var(--border-color); 
            box-shadow: 0 12px 40px rgba(0,0,0,0.3); 
            border-radius: 20px; 
            color: var(--text-main);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .card:hover { 
            transform: translateY(-4px); 
            border-color: rgba(14, 165, 233, 0.4);
            box-shadow: 0 20px 40px rgba(14, 165, 233, 0.15);
        }
        
        .btn-primary { 
            background: linear-gradient(135deg, var(--accent-glow), #0284c7); 
            border: none; 
            font-weight: 700; 
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(14, 165, 233, 0.3);
            transition: all 0.2s;
        }
        .btn-primary:hover { 
            background: linear-gradient(135deg, #0284c7, #0369a1);
            transform: translateY(-2px);
            box-shadow: 0 6px 22px rgba(14, 165, 233, 0.4);
        }
        
        .btn-success { 
            background: linear-gradient(135deg, var(--accent-success), #059669); 
            border: none; 
            font-weight: 700; 
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
        }
        
        .form-control, .form-select { 
            background-color: #060a14;
            border-radius: 12px; 
            border: 1px solid var(--border-color); 
            padding: 14px 18px; 
            color: var(--text-main);
        }
        .form-control:focus, .form-select:focus { 
            background-color: #060a14;
            color: var(--text-main);
            border-color: var(--accent-glow); 
            box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.2); 
        }
        
        .alert {
            background-color: var(--bg-card);
            border-left: 4px solid var(--accent-glow) !important;
            color: var(--text-main);
            border-radius: 14px;
        }

        .table-cyber {
            background-color: transparent !important;
            color: var(--text-main) !important;
        }
        .table-cyber tr {
            border-bottom: 1px solid var(--border-color) !important;
            background: transparent !important;
        }
        .table-cyber th {
            background-color: #060a14 !important;
            color: var(--accent-glow) !important;
            border-bottom: 2px solid var(--border-color) !important;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }
        .table-cyber td {
            background-color: transparent !important;
            color: var(--text-main) !important;
            padding: 16px 12px !important;
        }
        
        footer { 
            background-color: #04060d; 
            color: var(--text-muted); 
            padding: 45px 0; 
            margin-top: 100px; 
            border-top: 1px solid var(--border-color); 
        }
        
        .accent-gradient-text {
            background: linear-gradient(to right, #0ea5e9, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Large Separate Dedicated Welcome Section Styles */
        .dedicated-welcome-strip {
            background: linear-gradient(90deg, rgba(14, 165, 233, 0.15), rgba(168, 85, 247, 0.05));
            border-bottom: 1px solid rgba(14, 165, 233, 0.15);
            padding: 24px 0;
            margin-top: 80px; /* Positions below fixed header */
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top py-3">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center gap-2" href="{{ url_for('index') }}">🤝 <span>Community Hub</span></a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <div class="navbar-nav ms-auto align-items-center gap-3">
                    {% if current_user.is_authenticated and current_user.is_admin %}
                        <a class="nav-link text-warning fw-extrabold px-2" href="{{ url_for('admin') }}">🛠 MAIN DECK</a>
                        <a class="nav-link text-info fw-extrabold px-2" href="{{ url_for('admin_volunteers') }}">📋 APPROVE VOLUNTEERS</a>
                    {% endif %}
                    
                    <a class="nav-link text-white-50 px-2" href="{{ url_for('index') }}">View Requests</a>
                    <a class="nav-link text-white-50 px-2" href="{{ url_for('volunteers') }}">Volunteers</a>
                    
                    {% if current_user.is_authenticated %}
                        <a class="nav-link text-white-50 px-2" href="{{ url_for('help_request') }}">Request Help Form</a>
                        <a class="nav-link text-white-50 px-2" href="{{ url_for('feedback') }}">Feedback</a>
                        <a class="btn btn-outline-light btn-sm px-3 rounded-3 ms-1" href="{{ url_for('logout') }}">Logout</a>
                    {% else %}
                        <a class="btn btn-link text-white-50 text-decoration-none" href="{{ url_for('login') }}">Login</a>
                        <a class="btn btn-primary btn-sm px-4 py-2" href="{{ url_for('register') }}">Register</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <!-- SPACIOUS DEDICATED WELCOME DECK STRIP BELOW NAVBAR -->
    {% if current_user.is_authenticated %}
    <div class="dedicated-welcome-strip">
        <div class="container d-flex align-items-center justify-content-between">
            <div>
                <h4 class="mb-1 fw-bold text-white">System Environment Active</h4>
                <p class="mb-0 text-white-50 small">Secure verification tunnels operational.</p>
            </div>
            <div class="text-end">
                <span class="fs-5 text-white-50">👋 Welcome back, <strong class="accent-gradient-text" style="-webkit-text-fill-color: initial; background: linear-gradient(to right, #0ea5e9, #a855f7); -webkit-background-clip: text; font-weight: 800;">{{ current_user.name }}</strong>!</span>
            </div>
        </div>
    </div>
    {% endif %}

    <div class="container" style="margin-top: {% if current_user.is_authenticated %}30px{% else %}100px{% endif %};">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-dismissible fade show shadow-sm" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    {% block content %}{% endblock %}

    <footer class="text-center">
        <div class="container">
            <p class="mb-0 opacity-60">© 2026 Community Help Portal. Designed beautifully for dynamic social connections.</p>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

INDEX_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="hero-section">
    <div class="container">
        <h1 class="display-3 fw-extrabold mb-3" style="letter-spacing: -2px; font-weight: 800;">Connecting Neighbors.<br><span class="accent-gradient-text">Empowering Support.</span></h1>
        <p class="lead mb-4 mx-auto text-muted" style="max-width: 600px;">Review ongoing community updates below. Log in to broadcast an incident dispatch form.</p>
        <div class="d-flex justify-content-center gap-3 mb-5">
            {% if current_user.is_authenticated %}
                <a href="{{ url_for('help_request') }}" class="btn btn-primary btn-lg px-5 py-3 shadow-lg">Submit A Help Request</a>
            {% else %}
                <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg px-5 py-3 shadow-lg">Sign In to Request Help</a>
            {% endif %}
        </div>
    </div>
</div>

<div class="container my-5">
    {% if current_user.is_authenticated and active_notifications %}
        <div class="row justify-content-center mb-4">
            <div class="col-md-9">
                <div class="card p-4 border border-warning" style="background-color: #1a1614;">
                    <h5 class="text-warning fw-bold mb-3">⚡ Operational Request Matches Detected:</h5>
                    <ul class="text-white-50 mb-0 ps-3">
                        {% for notice in active_notifications %}
                            <li class="mb-2">User <strong class="text-white">{{ notice.username }}</strong> requested help under your category: <span class="badge bg-warning text-dark fw-bold">{{ notice.category }}</span></li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    {% endif %}

    <div class="row justify-content-center mb-4">
        <div class="col-md-8">
            <div class="card p-3 shadow-sm" style="background-color: #0e1626;">
                <form method="GET" action="{{ url_for('index') }}" class="d-flex gap-2">
                    <input type="text" name="s" class="form-control" placeholder="🔍 Search through active requests..." value="{{ search_query }}">
                    <button type="submit" class="btn btn-primary px-4">Search</button>
                    {% if search_query %}
                        <a href="{{ url_for('index') }}" class="btn btn-outline-secondary text-white border-secondary">Clear</a>
                    {% endif %}
                </form>
            </div>
        </div>
    </div>

    <div class="row justify-content-center">
        <div class="col-md-9">
            <h2 class="fw-bold mb-4 text-center text-md-start" style="font-weight: 800;">🚨 Active Community Incident Board</h2>
            {% if request_data %}
                <div class="row g-3">
                {% for item in request_data %}
                    <div class="col-12">
                        <div class="card p-4 border-start border-info border-4 shadow-md" style="background-color: #0d1527;">
                            <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                                <div>
                                    <h4 class="fw-bold text-info mb-1">{{ item.request.title }}</h4>
                                    <div class="mb-2">
                                        <span class="badge bg-primary text-white me-2">{{ item.request.category }}</span>
                                        <span class="text-muted small">Posted by: <strong>{{ item.request.username }}</strong></span>
                                    </div>
                                </div>
                                <span class="badge bg-secondary font-monospace" style="font-size: 0.75rem;">{{ item.request.created_at.strftime('%Y-%m-%d') }}</span>
                            </div>
                            <p class="text-white-50 my-2">{{ item.request.description }}</p>
                            
                            <div class="mt-2 pt-2 border-top border-secondary border-opacity-20">
                                <span class="text-muted small">✉️ Contact Channels:</span>
                                {% if item.has_access %}
                                    <strong class="text-success small font-monospace ms-1">{{ item.request.contact }}</strong>
                                {% else %}
                                    <span class="text-white-50 small fst-italic ms-1" style="font-size: 0.85rem; color: #ef4444 !important;">🔒 Hidden. Locked until a verified matching category volunteer agent logs in.</span>
                                {% endif %}
                            </div>
                            
                            <div class="mt-3 p-3 rounded" style="background-color: #060a14; border: 1px solid var(--border-color);">
                                <h6 class="text-white fw-bold mb-2" style="font-size: 0.85rem;">🛡️ Match Matrix Strategy Status:</h6>
                                {% if item.matches %}
                                    <div class="d-flex flex-wrap gap-2">
                                        {% for match in item.matches %}
                                            <span class="badge bg-success-subtle text-success border border-success px-2 py-1">⚡ Agent Vetted: {{ match.name }}</span>
                                        {% endfor %}
                                    </div>
                                {% else %}
                                    <span class="text-warning small fst-italic">⚠️ No match found yet</span>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                {% endfor %}
                </div>
            {% else %}
                <div class="text-muted p-5 rounded-4 text-center border border-dashed border-secondary">
                    No matching community help parameters identified in data registers.
                </div>
            {% endif %}
        </div>
    </div>
</div>
""")

LOGIN_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container my-5 py-5">
    <div class="row justify-content-center">
        <div class="col-md-5">
            <div class="card p-4 p-md-5">
                <h2 class="fw-bold mb-2 text-center">Welcome Back</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Email Address</label>
                        <input type="email" name="email" class="form-control" placeholder="name@example.com" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-semibold text-white-50">Password</label>
                        <input type="password" name="password" class="form-control" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 py-3">Sign In</button>
                </form>
            </div>
        </div>
    </div>
</div>
""")

REGISTER_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container my-5 py-5">
    <div class="row justify-content-center">
        <div class="col-md-5">
            <div class="card p-4 p-md-5">
                <h2 class="fw-bold mb-2 text-center">Create Profile</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Full Name</label>
                        <input type="text" name="name" class="form-control" placeholder="John Doe" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Email Address</label>
                        <input type="email" name="email" class="form-control" placeholder="name@example.com" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-semibold text-white-50">Password</label>
                        <input type="password" name="password" class="form-control" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 py-3">Sign Up</button>
                </form>
            </div>
        </div>
    </div>
</div>
""")

HELP_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container my-5 py-4">
    <div class="row justify-content-center">
        <div class="col-md-7">
            <div class="card p-4 p-md-5">
                <h2 class="mb-4 text-center fw-bold">Submit Help Dispatch Form</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Category Matrix Classification</label>
                        <select name="category" class="form-select" required>
                            {% for cat in categories %}
                                <option value="{{ cat }}">{{ cat }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">What do you need help with? (Title)</label>
                        <input type="text" name="title" class="form-control" placeholder="e.g., Grocery target delivery" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Detailed Description</label>
                        <textarea name="description" class="form-control" rows="5" required></textarea>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-semibold text-white-50">Contact Routing Information</label>
                        <input type="text" name="contact" class="form-control" placeholder="Phone target sequence or secure email" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 py-3">Broadcast Request</button>
                </form>
            </div>
        </div>
    </div>
</div>
""")

VOLUNTEER_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container my-5 py-4">
    <div class="row g-5">
        <div class="col-md-5">
            <div class="card p-4 shadow-sm">
                <h3 class="fw-bold mb-4">Volunteer Entry</h3>
                {% if current_user.is_authenticated %}
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Operational Core Category</label>
                        <select name="category" class="form-select" required>
                            {% for cat in categories %}
                                <option value="{{ cat }}">{{ cat }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Your Name</label>
                        <input type="text" name="name" class="form-control" value="{{ current_user.name }}" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Your Email</label>
                        <input type="email" name="email" class="form-control" value="{{ current_user.email }}" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-semibold text-white-50">Skills & Structural Assets</label>
                        <textarea name="skills" class="form-control" rows="3" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-success w-100 py-3">Submit Assets</button>
                </form>
                {% else %}
                <div class="text-center py-4">
                    <p class="text-muted small">Please log in to register as an operational volunteer agent.</p>
                    <a href="{{ url_for('login') }}" class="btn btn-primary w-100">Login Now</a>
                </div>
                {% endif %}
            </div>
        </div>
        <div class="col-md-7">
            <h3 class="fw-bold mb-4">Verified Network Responders</h3>
            {% if volunteers %}
                <div class="row g-3">
                {% for v in volunteers %}
                    <div class="col-12">
                        <div class="card p-4 border-start border-success border-4">
                            <h5 class="fw-bold mb-1 text-success">🌟 {{ v.name }}</h5>
                            <span class="badge bg-dark border border-success text-success mb-2 align-self-start" style="width: fit-content;">{{ v.category }}</span>
                            <p class="mb-0 text-white-50 small"><strong>Capabilities:</strong> {{ v.skills }}</p>
                        </div>
                    </div>
                {% endfor %}
                </div>
            {% else %}
                <div class="text-muted p-5 rounded-4 text-center border border-dashed border-secondary">
                    No verified active agents matched in data matrix yet.
                </div>
            {% endif %}
        </div>
    </div>
</div>
""")

FEEDBACK_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container my-5 py-4">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card p-4 p-md-5">
                <h2 class="text-center fw-bold mb-4">System Analytics Feedback</h2>
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-white-50">Your Name</label>
                        <input type="text" name="name" class="form-control" value="{{ current_user.name }}" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-semibold text-white-50">Observations</label>
                        <textarea name="message" class="form-control" rows="4" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 py-3">Submit Metrics</button>
                </form>
            </div>
        </div>
    </div>
</div>
""")

MAIN_ADMIN_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container-fluid my-4 px-4 py-4">
    <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
        <h1 class="text-white mb-0" style="font-weight: 800; letter-spacing: -1.5px; text-shadow: 0 4px 12px rgba(14,165,233,0.3);">🛠 COMMAND CONTROLS DECK</h1>
        <a href="{{ url_for('admin_volunteers') }}" class="btn btn-info py-2.5 px-4 shadow-md" style="font-weight: 700;">Open Volunteer Approvals Deck ➔</a>
    </div>
    
    <div class="row g-4">
        <div class="col-md-6">
            <div class="card p-4 h-100 shadow-sm" style="border-top: 4px solid var(--accent-glow);">
                <h3 class="mb-3 text-info" style="font-weight: 800;">🚨 LIVE INCIDENT STREAM</h3>
                <div class="list-group mt-2 bg-transparent">
                    {% for r in requests %}
                        <div class="list-group-item p-3 mb-2 rounded-3 border-0" style="background-color: #0f172a; border: 1px solid #1e294b !important;">
                            <div class="d-flex justify-content-between align-items-start">
                                <h5 class="mb-1 text-info" style="font-weight: 700;">{{ r.title }}</h5>
                                <span class="badge bg-primary text-white font-monospace" style="font-size:0.7rem;">{{ r.category }}</span>
                            </div>
                            <p class="mb-1 text-white-50 small">{{ r.description }}</p>
                            <small class="text-muted d-block small">Author Node: <strong>{{ r.username }}</strong></small>
                            <small class="text-muted d-block font-monospace mt-1" style="font-size: 0.75rem;">Routing Payload: {{ r.contact }}</small>
                        </div>
                    {% else %}
                        <p class="text-muted text-center my-4 small">No tracking requests in live registers.</p>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card p-4 h-100 shadow-sm" style="border-top: 4px solid var(--accent-purple);">
                <h3 class="mb-3 text-purple" style="color: var(--accent-purple); font-weight: 800;">💬 DATA ANALYTICS FEEDBACK</h3>
                <div class="list-group mt-2 bg-transparent">
                    {% for f in feedbacks %}
                        <div class="list-group-item p-3 mb-2 rounded-3 border-0" style="background-color: #0f172a; border: 1px solid #1e294b !important;">
                            <strong class="text-white" style="font-weight: 700;">👤 {{ f.name }}</strong>
                            <p class="mb-0 mt-1 text-white-50 small fst-italic">"{{ f.message }}"</p>
                        </div>
                    {% else %}
                        <p class="text-muted text-center my-4 small">No user experience observations stored.</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
""")

VOLUNTEER_ADMIN_HTML = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
<div class="container-fluid my-4 px-4 py-4">
    <div class="d-flex align-items-center gap-3 mb-4">
        <a href="{{ url_for('admin') }}" class="btn btn-outline-secondary text-white border-secondary px-3 py-2">⬅ Back</a>
        <h1 class="text-white mb-0" style="font-weight: 800; letter-spacing: -1.5px; text-shadow: 0 4px 12px rgba(16,185,129,0.3);">📋 AGENT VERIFICATION DECK</h1>
    </div>

    <div class="row">
        <div class="col-12">
            <div class="card p-4 shadow-lg" style="background-color: var(--bg-card); border: 1px solid var(--border-color);">
                <h3 class="mb-3 text-white" style="font-weight: 800;">🔒 VOLUNTEER SECURITY MATRIX DIRECTORY</h3>
                <div class="table-responsive">
                    <table class="table table-cyber align-middle mb-0">
                        <thead>
                            <tr>
                                <th class="py-3">Node Name</th>
                                <th class="py-3">Email Matrix</th>
                                <th class="py-3">Operational Target Tag</th>
                                <th class="py-3">Asset Declarations</th>
                                <th class="py-3">Status Matrix</th>
                                <th class="py-3">Execution Trigger</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for v in volunteers %}
                            <tr>
                                <td><strong style="font-weight: 700; color: #e2e8f0;">{{ v.name }}</strong></td>
                                <td class="text-white-50">{{ v.email }}</td>
                                <td><span class="badge bg-secondary">{{ v.category }}</span></td>
                                <td class="text-white-50">{{ v.skills }}</td>
                                <td>
                                    {% if v.approved %}
                                        <span class="badge bg-success text-white px-3 py-2 rounded-3" style="font-weight: 700;">ACTIVE OPERATION</span>
                                    {% else %}
                                        <span class="badge bg-warning text-dark px-3 py-2 rounded-3" style="font-weight: 700;">PENDING AUTH</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if not v.approved %}
                                        <a href="{{ url_for('approve_volunteer', volunteer_id=v.id) }}" class="btn btn-sm btn-success px-4 py-2 shadow-sm" style="font-weight: 800;">VERIFY AGENT</a>
                                    {% else %}
                                        <button class="btn btn-sm btn-outline-secondary px-3 text-muted" style="border-color: var(--border-color);" disabled>VETTED</button>
                                    {% endif %}
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="6" class="text-center text-muted py-4">No agents populated in matrix directory.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
""")

# ==========================================
# ROUTING CONTROLLERS
# ==========================================
@app.route("/")
def index():
    search_query = request.args.get('s', '')
    if search_query:
        req_list = HelpRequest.query.filter(
            (HelpRequest.title.contains(search_query)) | 
            (HelpRequest.description.contains(search_query)) |
            (HelpRequest.category.contains(search_query))
        ).order_by(HelpRequest.created_at.desc()).all()
    else:
        req_list = HelpRequest.query.order_by(HelpRequest.created_at.desc()).all()
        
    user_authorized_categories = set()
    if current_user.is_authenticated:
        if current_user.is_admin:
            for cat in CATEGORIES:
                user_authorized_categories.add(cat)
        else:
            user_v_profiles = Volunteer.query.filter_by(email=current_user.email, approved=True).all()
            for profile in user_v_profiles:
                user_authorized_categories.add(profile.category)

    request_data = []
    for r in req_list:
        matched_agents = Volunteer.query.filter_by(category=r.category, approved=True).all()
        has_access = (len(matched_agents) > 0) and (r.category in user_authorized_categories)
        
        request_data.append({
            'request': r,
            'matches': matched_agents,
            'has_access': has_access
        })

    active_notifications = []
    if current_user.is_authenticated and not current_user.is_admin:
        v_profiles = Volunteer.query.filter_by(email=current_user.email, approved=True).all()
        for vp in v_profiles:
            matching_requests = HelpRequest.query.filter_by(category=vp.category).all()
            for mr in matching_requests:
                active_notifications.append({
                    'category': mr.category,
                    'username': mr.username
                })
        
    return render_template_string(INDEX_HTML, request_data=request_data, search_query=search_query, active_notifications=active_notifications)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            if user.is_admin:
                return redirect(url_for("admin"))
            return redirect(url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template_string(LOGIN_HTML)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))
            
        hashed_pw = generate_password_hash(password)
        
        if email.strip().lower() == "sanjanapoojary402@gmail.com":
            is_admin_user = True
        else:
            is_admin_user = False
            
        new_user = User(name=name, email=email, password=hashed_pw, is_admin=is_admin_user)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template_string(REGISTER_HTML)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))

@app.route("/help-request", methods=["GET", "POST"])
@login_required
def help_request():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description")
        contact = request.form.get("contact")
        
        new_request = HelpRequest(
            user_id=current_user.id,
            username=current_user.name,
            title=title, 
            category=category, 
            description=description, 
            contact=contact
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Help request submitted successfully!", "success")
        return redirect(url_for("index"))
    return render_template_string(HELP_HTML, categories=CATEGORIES)

@app.route("/volunteers", methods=["GET", "POST"])
def volunteers():
    if request.method == "POST":
        if not current_user.is_authenticated:
            abort(401)
        name = request.form.get("name")
        email = request.form.get("email")
        category = request.form.get("category")
        skills = request.form.get("skills")
        
        new_volunteer = Volunteer(name=name, email=email, category=category, skills=skills, approved=False)
        db.session.add(new_volunteer)
        db.session.commit()
        flash("Application submitted! Awaiting admin approval.", "success")
        return redirect(url_for("index"))
    approved_list = Volunteer.query.filter_by(approved=True).all()
    return render_template_string(VOLUNTEER_HTML, volunteers=approved_list, categories=CATEGORIES)

@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")
        new_fb = Feedback(name=name, message=message)
        db.session.add(new_fb)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
        return redirect(url_for("index"))
    return render_template_string(FEEDBACK_HTML)

@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    all_requests = HelpRequest.query.order_by(HelpRequest.created_at.desc()).all()
    all_feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template_string(MAIN_ADMIN_HTML, requests=all_requests, feedbacks=all_feedback)

@app.route("/admin/volunteers")
@login_required
def admin_volunteers():
    if not current_user.is_admin:
        abort(403)
    all_volunteers = Volunteer.query.order_by(Volunteer.created_at.desc()).all()
    return render_template_string(VOLUNTEER_ADMIN_HTML, volunteers=all_volunteers)

@app.route("/admin/approve/<int:volunteer_id>")
@login_required
def approve_volunteer(volunteer_id):
    if not current_user.is_admin:
        abort(403)
    volunteer = Volunteer.query.get_or_404(volunteer_id)
    volunteer.approved = True
    db.session.commit()
    flash("Volunteer approved successfully.", "success")
    return redirect(url_for('admin_volunteers'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)