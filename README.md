# telegram-chatbot-admin

This project is a Telegram chatbot with an admin dashboard and REST API for managing users, chat sessions, and system settings. The bot interacts with users through Telegram, while the web application provides an interface for administrators, and the REST API enables programmatic access for external integrations.

## Project Structure

```
ibs_info_chatbot
├── src
│   ├── api                # REST API Module
│   │   ├── __init__.py
│   │   ├── app.py         # API Flask app factory
│   │   └── v1             # API Version 1
│   │       ├── __init__.py
│   │       ├── middleware # API Middleware
│   │       │   ├── __init__.py
│   │       │   ├── auth.py           # JWT authentication
│   │       │   ├── cors.py           # CORS configuration
│   │       │   └── error_handler.py  # Error handling
│   │       ├── routes     # API Routes
│   │       │   ├── admins.py         # Admin CRUD endpoints
│   │       │   ├── auth.py           # Authentication endpoints
│   │       │   ├── chats.py          # Chat session endpoints
│   │       │   ├── dashboard.py      # Dashboard statistics
│   │       │   ├── system_settings.py # FAQ/Category management
│   │       │   └── users.py          # User CRUD endpoints
│   │       └── schemas    # Request/Response schemas
│   │           ├── __init__.py
│   │           ├── admin_schema.py
│   │           ├── chat_schema.py
│   │           ├── response_schema.py
│   │           ├── system_setting_schema.py
│   │           └── user_schema.py
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
│   │       ├── recreate_sessions_messages.py
│   │       ├── seed_categories.py
│   │       ├── seed_faqs.py
│   │       ├── seed_super_admin.py
│   │       ├── seed_users.py
│   │       ├── seed_chat_sessions.py
│   │       └── seed_chat_messages.py
│   ├── services           # Business logic layer (shared by Web & API)
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
│       ├── helpers.py     # Helper functions
│       └── jwt_helper.py  # JWT token utilities
├── requirements.txt       # Project dependencies
├── .env.example           # Example environment variables
├── .env                   # Environment variables (not in git)
├── .gitignore             # Files to ignore in version control
├── run_all.py             # Script to run all services together
├── run_api.py             # Script to run the REST API
├── run_bot.py             # Script to run the Telegram bot
├── run_web.py             # Script to run the web application
├── API_DOCUMENTATION.md   # Complete API documentation
└── planning.md            # Project restructure plan
```

## Features

### 🤖 Telegram Bot
- User registration and authentication
- FAQ system with categories
- Live chat with admins
- Session management

### 🌐 Web Application (Admin Dashboard)
- Admin authentication
- User management (CRUD)
- Admin management (CRUD)
- Live chat interface
- Dashboard with statistics
- FAQ and category management
- Real-time updates via WebSocket

### 🔌 REST API
- JWT-based authentication
- Complete CRUD operations for:
  - Users
  - Admins
  - Chat sessions
  - Messages
  - FAQs and categories
- Dashboard analytics endpoints
- Role-based access control
- CORS support for frontend integration
- Comprehensive error handling

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ibs_info_chatbot
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and filling in the required values:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Database Setup

### 1. Initialize the database
```bash
python -m src.database.migrations.init_db
```

### 2. Recreate tables (if needed)
```bash
python -m src.database.migrations.recreate_tables
```

### 3. Seed initial data

**Create super admin:**
```bash
python -m src.database.migrations.seed_super_admin
```

**Create FAQ categories:**
```bash
python -m src.database.migrations.seed_categories
```

**Create FAQs:**
```bash
python -m src.database.migrations.seed_faqs
```

**Create test users:**
```bash
python -m src.database.migrations.seed_users
```

**Create test chat sessions:**
```bash
python -m src.database.migrations.seed_chat_sessions
```

**Create test messages:**
```bash
python -m src.database.migrations.seed_chat_messages
```

## 🚀 Running the Application

### Option 1: Run All Services Together
```bash
python run_all.py
```

This starts:
- Web Application (Admin Dashboard) on `http://localhost:5000`
- REST API on `http://localhost:5001`
- Telegram Bot

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
# API Documentation: http://localhost:5001/api
```

**Telegram Bot:**
```bash
python run_bot.py
# Connects to Telegram
```

## Configuration

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

# JWT Configuration
JWT_SECRET_KEY=your-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 days

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS

# Database
DATABASE_URL=mysql+pymysql://user:pass@localhost/db_name

# Telegram Bot
BOT_TOKEN=your-telegram-bot-token
BOT_USERNAME=your-bot-username
```

## API Documentation

Complete API documentation is available in [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md).

### Quick API Overview

**Base URL:** `http://localhost:5001/api/v1`

**Authentication:**
```bash
# Login
POST /api/v1/auth/login
Body: {"telegram_id": "123456789"}

# Use token in subsequent requests
Authorization: Bearer <access_token>
```

**Example Endpoints:**
- `GET /api/v1/users` - List users
- `GET /api/v1/admins` - List admins
- `GET /api/v1/chats` - List chat sessions
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/settings/categories` - List FAQ categories
- `GET /api/v1/settings/faqs` - List FAQs

For complete endpoint documentation with request/response examples, see [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md).

## Architecture

### Service Layer Pattern
The application uses a shared service layer that is accessed by both the web application and REST API:

```
┌─────────────┐         ┌─────────────┐
│ Web Routes  │         │ API Routes  │
└──────┬──────┘         └──────┬──────┘
       │                       │
       └───────┬───────────────┘
               │
         ┌─────▼──────┐
         │  Services  │
         └─────┬──────┘
               │
         ┌─────▼──────┐
         │  Database  │
         └────────────┘
```

### Key Benefits
- ✅ **Reusable Logic** - Business logic shared between web and API
- ✅ **Consistent Data Access** - Same service methods for both interfaces
- ✅ **Easy Maintenance** - Changes in one place affect both web and API
- ✅ **Separation of Concerns** - Clear boundaries between layers

## Development

### Project Structure Explanation

- **`src/api/`** - REST API module with JWT authentication
- **`src/bot/`** - Telegram bot handlers and keyboards
- **`src/web/`** - Web application (admin dashboard)
- **`src/services/`** - Shared business logic layer
- **`src/database/`** - Database models and migrations
- **`src/utils/`** - Utility functions and configuration

### Adding New Features

1. **Add Service Method** - Create business logic in appropriate service
2. **Add Web Route** (optional) - Create web route in `src/web/routes/`
3. **Add API Route** (optional) - Create API endpoint in `src/api/v1/routes/`
4. **Add Schema** (for API) - Create validation schema in `src/api/v1/schemas/`

## Testing

### Manual API Testing

**Using cURL:**
```bash
# Login
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": "123456789"}'

# List users (with token)
curl -X GET http://localhost:5001/api/v1/users \
  -H "Authorization: Bearer <your_token>"
```

**Using Postman/Thunder Client:**
- Import the API collection from `API_DOCUMENTATION.md`
- Set `Authorization` header: `Bearer <token>`
- Test all endpoints

## License

[Your License Here]

## Contributors

[Your Name/Team]

## Support

For issues and questions, please open an issue on GitHub.
