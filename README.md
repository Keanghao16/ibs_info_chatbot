# telegram-chatbot-admin

This project is a Telegram chatbot with an admin dashboard for managing users and viewing chat history. The bot interacts with users through Telegram, while the web application provides an interface for administrators to manage the chatbot's functionalities.

## Project Structure

```
ibs_info_chatbot
├── src
│   ├── bot                # Telegram bot logic
│   │   ├── __init__.py
│   │   ├── main.py        # Entry point for the bot
│   │   ├── handlers       # Bot command and message handlers
│   │   │   ├── callback.py
│   │   │   ├── message.py
│   │   │   └── start.py
│   │   └── keyboards      # Inline keyboards for user interactions
│   │       ├── __init__.py
│   │       └── inline.py
│   ├── web                # Web application for admin dashboard
│   │   ├── __init__.py
│   │   ├── app.py         # Flask application setup
│   │   ├── websocket_manager.py  # WebSocket connection management
│   │   ├── routes         # Web routes organization
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── chats.py
│   │   │   ├── dashboard.py
│   │   │   ├── system_settings.py
│   │   │   └── users.py
│   │   ├── static         # Static assets
│   │   │   ├── css
│   │   │   │   └── style.css
│   │   │   └── js
│   │   │       └── dashboard.js
│   │   └── templates      # HTML templates
│   │       ├── master.html
│   │       ├── admin      # Admin management pages
│   │       │   ├── edit.html
│   │       │   ├── index.html
│   │       │   └── view.html
│   │       ├── auth       # Authentication pages
│   │       │   ├── login.html
│   │       │   └── profile.html
│   │       ├── chat       # Chat interface
│   │       │   ├── index.html
│   │       │   └── live_chat.html
│   │       ├── dashboard  # Dashboard pages
│   │       │   └── index.html
│   │       ├── system_setting  # System settings
│   │       │   └── index.html
│   │       └── user       # User management pages
│   │           ├── index.html
│   │           └── view.html
│   ├── database           # Database connection and models
│   │   ├── __init__.py
│   │   ├── connection.py  # Database connection setup
│   │   ├── models.py      # SQLAlchemy models
│   │   └── migrations     # Database migration scripts
│   │       ├── __init__.py
│   │       ├── init_db.py
│   │       ├── recreate_tables.py
│   │       ├── seed_categories.py
│   │       ├── seed_faqs.py
│   │       └── seed_super_admin.py
│   ├── services           # Business logic layer
│   │   ├── __init__.py
│   │   ├── admin_service.py
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── dashboard_service.py
│   │   ├── faq_service.py
│   │   ├── system_setting_service.py
│   │   └── user_service.py
│   └── utils              # Utility functions and configuration
│       ├── __init__.py
│       ├── config.py      # Configuration management
│       └── helpers.py     # Helper functions
├── requirements.txt       # Project dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Files to ignore in version control
├── run_bot.py             # Script to run the Telegram bot
├── run_web.py             # Script to run the web application
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ibs_info_chatbot
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and filling in the required values.

## Database Setup

### Initialize the database
```bash
python -m src.database.migrations.init_db
```

### Recreate tables (if needed)
```bash
python -m src.database.migrations.recreate_tables
```

### Seed initial data

1. Create super admin:
   ```bash
   python -m src.database.migrations.seed_super_admin
   ```

2. Create FAQ categories:
   ```bash
   python -m src.database.migrations.seed_categories
   ```

3. Create FAQs:
   ```bash
   python -m src.database.migrations.seed_faqs
   ```

4. Create users:
   ```bash
   python -m src.database.migrations.seed_users
   ```

## Running the Bot

To run the Telegram bot, execute the following command:
```bash
python run_bot.py
```

## Running the Web Application

To run the admin dashboard, execute the following command:
```bash
python run_web.py
```

## 🚀 Running the Application

### Option 1: Run All Services Together
```bash
python run_all.py
```

### Option 2: Run Services Individually

**Web Application (Admin Dashboard):**
```bash
python run_web.py
# Runs on http://localhost:5000
```

**REST API:**
```bash
python run_api.py
# Runs on http://localhost:5001
```

**Telegram Bot:**
```bash
python run_bot.py
# Connects to Telegram
```

### Configuration

All ports and settings are configured in the `.env` file:

```env
# Web Application
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_DEBUG=True

# REST API
API_HOST=0.0.0.0
API_PORT=5001
API_DEBUG=True
```

To change ports, simply update the values in your `.env` file.
