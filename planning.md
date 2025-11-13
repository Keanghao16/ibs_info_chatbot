# Project Restructure Plan: Adding REST API Support

## Overview
Convert the existing web application to support both traditional web routes (HTML) and REST API endpoints (JSON) by restructuring the project architecture.

---

## Current Structure Analysis

### Existing Components
- **Web Routes**: [`src/web/routes/`](src/web/routes/) - Returns HTML templates
- **Services Layer**: [`src/services/`](src/services/) - Business logic (reusable)
- **Database Models**: [`src/database/models.py`](src/database/models.py) - SQLAlchemy models
- **Bot**: [`src/bot/`](src/bot/) - Telegram bot handlers

### Key Finding
✅ **Good News**: The service layer is already separated, making it easy to reuse for API!

---

## Target Structure

```
ibs_info_chatbot/
├── src/
│   ├── api/                           # ✨ NEW: REST API Module
│   │   ├── __init__.py
│   │   ├── app.py                     # API Flask app factory
│   │   ├── v1/                        # API Version 1
│   │   │   ├── __init__.py
│   │   │   ├── routes/                # API Routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py           # POST /api/v1/auth/login
│   │   │   │   ├── users.py          # CRUD /api/v1/users
│   │   │   │   ├── admins.py         # CRUD /api/v1/admins
│   │   │   │   ├── chats.py          # CRUD /api/v1/chats
│   │   │   │   ├── dashboard.py      # GET /api/v1/dashboard/stats
│   │   │   │   └── system_settings.py # CRUD /api/v1/settings
│   │   │   ├── middleware/            # API Middleware
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py           # JWT authentication
│   │   │   │   ├── cors.py           # CORS configuration
│   │   │   │   └── error_handler.py  # Error handling
│   │   │   └── schemas/               # Request/Response validation
│   │   │       ├── __init__.py
│   │   │       ├── user_schema.py
│   │   │       ├── admin_schema.py
│   │   │       ├── chat_schema.py
│   │   │       └── response_schema.py
│   │   └── v2/                        # Future API versions
│   │
│   ├── bot/                           # ✅ Keep as is
│   │   └── ...
│   │
│   ├── web/                           # ✅ Keep web application
│   │   ├── app.py                     # Web Flask app
│   │   ├── routes/                    # Web routes (HTML)
│   │   └── templates/
│   │
│   ├── services/                      # ✅ Shared by both Web & API
│   │   ├── user_service.py
│   │   ├── admin_service.py
│   │   ├── chat_service.py
│   │   └── ...
│   │
│   ├── database/                      # ✅ Shared database layer
│   │   ├── models.py
│   │   └── connection.py
│   │
│   └── utils/                         # ✅ Shared utilities
│       ├── config.py
│       ├── helpers.py
│       └── jwt_helper.py              # ✨ NEW: JWT utilities
│
├── run_web.py                         # Web application entry point
├── run_api.py                         # ✨ NEW: API entry point
├── run_bot.py                         # Bot entry point
├── requirements.txt                   # Update with new dependencies
└── planning.md                        # This file
```

---

## Implementation Plan

### Phase 1: Setup & Dependencies (Day 1)

#### 1.1 Install New Dependencies
```bash
pip install flask-restful flask-cors pyjwt marshmallow marshmallow-sqlalchemy
```

#### 1.2 Update requirements.txt
Add:
- `flask-restful==0.3.10` - REST API framework
- `flask-cors==4.0.0` - CORS support
- `PyJWT==2.8.0` - JWT authentication
- `marshmallow==3.20.1` - Object serialization/validation
- `marshmallow-sqlalchemy==0.29.0` - SQLAlchemy integration

#### 1.3 Create Directory Structure
```bash
mkdir -p src/api/v1/routes
mkdir -p src/api/v1/middleware
mkdir -p src/api/v1/schemas
touch src/api/__init__.py
touch src/api/app.py
touch src/api/v1/__init__.py
```

---

### Phase 2: Core API Infrastructure (Day 1-2)

#### 2.1 Create API App Factory
**File**: `src/api/app.py`

**Purpose**: Initialize Flask app for API with CORS, error handling, and middleware

**Key Features**:
- CORS configuration
- JSON error responses
- API versioning support
- Blueprint registration

#### 2.2 Create Response Schema
**File**: `src/api/v1/schemas/response_schema.py`

**Purpose**: Standardized JSON response format

**Response Structure**:
```json
{
  "success": true/false,
  "data": {},
  "message": "",
  "errors": [],
  "pagination": {}
}
```

#### 2.3 JWT Authentication Middleware
**File**: `src/api/v1/middleware/auth.py`

**Purpose**: Token-based authentication for API endpoints

**Features**:
- `@token_required` decorator
- Token validation
- User/Admin identification
- Role-based access control

#### 2.4 CORS Middleware
**File**: `src/api/v1/middleware/cors.py`

**Purpose**: Handle cross-origin requests

**Configuration**:
- Allowed origins
- Allowed methods (GET, POST, PUT, DELETE)
- Allowed headers

#### 2.5 Error Handler
**File**: `src/api/v1/middleware/error_handler.py`

**Purpose**: Consistent error responses

**Handle**:
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 500 Internal Server Error

#### 2.6 JWT Helper Utilities
**File**: `src/utils/jwt_helper.py`

**Purpose**: JWT token generation and validation

**Functions**:
- `generate_token(user_id, role)`
- `verify_token(token)`
- `decode_token(token)`

---

### Here
### Phase 3: Data Schemas (Day 2-3)

#### 3.1 User Schema
**File**: `src/api/v1/schemas/user_schema.py`

**Schemas**:
- `UserResponseSchema` - Serialize user data
- `UserCreateSchema` - Validate user creation
- `UserUpdateSchema` - Validate user updates

#### 3.2 Admin Schema
**File**: `src/api/v1/schemas/admin_schema.py`

**Schemas**:
- `AdminResponseSchema`
- `AdminCreateSchema`
- `AdminUpdateSchema`
- `AdminLoginSchema`

#### 3.3 Chat Schema
**File**: `src/api/v1/schemas/chat_schema.py`

**Schemas**:
- `ChatSessionResponseSchema`
- `ChatMessageResponseSchema`
- `MessageCreateSchema`

#### 3.4 System Settings Schema
**File**: `src/api/v1/schemas/system_setting_schema.py`

**Schemas**:
- `CategoryResponseSchema`
- `FAQResponseSchema`
- `FAQCreateSchema`

---

### Phase 4: API Routes Implementation (Day 3-5)

#### 4.1 Authentication Routes
**File**: `src/api/v1/routes/auth.py`

**Endpoints**:
```
POST   /api/v1/auth/login          - Login & get JWT token
POST   /api/v1/auth/logout         - Logout (invalidate token)
POST   /api/v1/auth/refresh        - Refresh JWT token
GET    /api/v1/auth/me             - Get current user info
```

**Reuse**: [`AuthService`](src/services/auth_service.py)

#### 4.2 Users Routes
**File**: `src/api/v1/routes/users.py`

**Endpoints**:
```
GET    /api/v1/users               - List all users (paginated)
GET    /api/v1/users/:id           - Get single user
POST   /api/v1/users               - Create new user
PUT    /api/v1/users/:id           - Update user
DELETE /api/v1/users/:id           - Delete user
GET    /api/v1/users/stats         - User statistics
POST   /api/v1/users/:id/promote   - Promote user to admin
```

**Reuse**: [`UserService`](src/services/user_service.py)

**Authentication**: `@token_required` - Admin only

#### 4.3 Admins Routes
**File**: `src/api/v1/routes/admins.py`

**Endpoints**:
```
GET    /api/v1/admins              - List all admins
GET    /api/v1/admins/:id          - Get single admin
POST   /api/v1/admins              - Create admin (super admin only)
PUT    /api/v1/admins/:id          - Update admin
DELETE /api/v1/admins/:id          - Delete admin (super admin only)
POST   /api/v1/admins/:id/demote   - Demote admin to user
PUT    /api/v1/admins/:id/toggle   - Toggle admin active status
PUT    /api/v1/admins/:id/availability - Toggle availability
GET    /api/v1/admins/stats        - Admin statistics
```

**Reuse**: [`AdminService`](src/services/admin_service.py)

**Authentication**: `@token_required` - Super Admin only (except stats)

#### 4.4 Chats Routes
**File**: `src/api/v1/routes/chats.py`

**Endpoints**:
```
GET    /api/v1/chats               - List all chat sessions
GET    /api/v1/chats/:id           - Get chat session details
POST   /api/v1/chats               - Create chat session
PUT    /api/v1/chats/:id/assign    - Assign admin to chat
POST   /api/v1/chats/:id/close     - Close chat session
GET    /api/v1/chats/:id/messages  - Get chat messages
POST   /api/v1/chats/:id/messages  - Send message
GET    /api/v1/chats/stats         - Chat statistics
```

**Reuse**: [`ChatService`](src/services/chat_service.py)

**Authentication**: `@token_required` - Admin only

#### 4.5 Dashboard Routes
**File**: `src/api/v1/routes/dashboard.py`

**Endpoints**:
```
GET    /api/v1/dashboard/stats     - Overall statistics
GET    /api/v1/dashboard/user-growth - User growth data
GET    /api/v1/dashboard/chat-trends - Chat trends
GET    /api/v1/dashboard/admin-performance - Admin performance
```

**Reuse**: [`DashboardService`](src/services/dashboard_service.py)

**Authentication**: `@token_required` - Admin only

#### 4.6 System Settings Routes
**File**: `src/api/v1/routes/system_settings.py`

**Endpoints**:
```
GET    /api/v1/settings/categories - List FAQ categories
POST   /api/v1/settings/categories - Create category
PUT    /api/v1/settings/categories/:id - Update category
DELETE /api/v1/settings/categories/:id - Delete category

GET    /api/v1/settings/faqs       - List FAQs
GET    /api/v1/settings/faqs/:id   - Get single FAQ
POST   /api/v1/settings/faqs       - Create FAQ
PUT    /api/v1/settings/faqs/:id   - Update FAQ
DELETE /api/v1/settings/faqs/:id   - Delete FAQ
```

**Reuse**: [`SystemSettingService`](src/services/system_setting_service.py)

**Authentication**: `@token_required` - Admin only

---

### Phase 5: API Entry Point (Day 5)

#### 5.1 Create run_api.py
**File**: `run_api.py`

```python
from src.api.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5001,  # Different port from web app
        debug=True
    )
```

#### 5.2 Update run_web.py
Keep web app running on port 5000

---

### Phase 6: Testing & Documentation (Day 6-7)

#### 6.1 API Testing
**Tools**: Postman or Thunder Client (VS Code extension)

**Test Cases**:
- Authentication flow
- CRUD operations for each resource
- Error handling
- Pagination
- Authorization (role-based access)

#### 6.2 API Documentation
**Create**: `API_DOCUMENTATION.md`

**Include**:
- Base URL
- Authentication guide
- All endpoints with examples
- Request/response formats
- Error codes

#### 6.3 Postman Collection
Export Postman collection for easy testing

---

## Database Modifications (if needed)

### Add Token Blacklist Table (Optional)
For logout functionality:

```python
class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'
    
    id = Column(Integer, primary_key=True)
    token = Column(String(500), unique=True, nullable=False)
    blacklisted_on = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
```

**Migration**: `src/database/migrations/add_token_blacklist.py`

---

## Environment Configuration

### Update .env
Add:
```env
# API Configuration
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
```

---

## Deployment Considerations

### Run Both Applications

**Option 1**: Separate Processes
```bash
# Terminal 1: Web App
python run_web.py

# Terminal 2: API
python run_api.py

# Terminal 3: Bot
python run_bot.py
```

**Option 2**: Process Manager (Production)
```bash
# Using PM2
pm2 start run_web.py --name "web-app"
pm2 start run_api.py --name "api"
pm2 start run_bot.py --name "telegram-bot"
```

**Option 3**: Docker Compose
Create separate containers for web, api, and bot

---

## Migration Strategy

### Gradual Migration
1. ✅ **Week 1**: Setup API infrastructure
2. ✅ **Week 2**: Implement core endpoints (auth, users, admins)
3. ✅ **Week 3**: Implement chat & dashboard endpoints
4. ✅ **Week 4**: Testing & documentation
5. ✅ **Week 5**: Production deployment

### No Downtime
- Web application continues running
- API runs on different port
- Shared database and services
- No breaking changes to existing web routes

---

## Testing Checklist

### API Functionality
- [ ] Authentication (login, logout, token refresh)
- [ ] User CRUD operations
- [ ] Admin CRUD operations
- [ ] Chat session management
- [ ] Message sending
- [ ] Dashboard statistics
- [ ] System settings management
- [ ] Pagination works correctly
- [ ] Filtering works correctly
- [ ] Sorting works correctly

### Security
- [ ] JWT token validation
- [ ] Role-based access control
- [ ] CORS configuration
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS prevention

### Performance
- [ ] Response time < 500ms
- [ ] Pagination for large datasets
- [ ] Database query optimization
- [ ] Proper error handling

### Documentation
- [ ] All endpoints documented
- [ ] Request/response examples
- [ ] Error codes documented
- [ ] Postman collection created

---

## Success Metrics

### Phase 1 Complete When:
- ✅ API app factory created
- ✅ JWT authentication working
- ✅ CORS configured
- ✅ Error handling implemented

### Phase 2 Complete When:
- ✅ All schemas defined
- ✅ Validation working
- ✅ Serialization working

### Phase 3 Complete When:
- ✅ All endpoints implemented
- ✅ All tests passing
- ✅ Documentation complete

### Final Success When:
- ✅ Web app still works
- ✅ API returns JSON responses
- ✅ Authentication works
- ✅ All CRUD operations work
- ✅ Can run both web & API simultaneously

---

## Future Enhancements (Post-MVP)

### API Versioning
- `/api/v2/` for breaking changes
- Maintain v1 for backward compatibility

### Rate Limiting
- Prevent API abuse
- Use `flask-limiter`

### API Keys (Alternative Auth)
- For machine-to-machine communication
- Generate API keys for external integrations

### Webhook Support
- Real-time event notifications
- Chat created, message received, etc.

### GraphQL API
- Alternative to REST
- More flexible queries

### API Monitoring
- Track usage
- Performance metrics
- Error rates

---

## Risk Mitigation

### Risk 1: Breaking Existing Web App
**Mitigation**: 
- Keep web routes completely separate
- Don't modify existing service layer interfaces
- Test web app after each change

### Risk 2: Authentication Conflicts
**Mitigation**:
- Use different session/token mechanisms
- Web: Flask sessions
- API: JWT tokens

### Risk 3: Database Performance
**Mitigation**:
- Add indexes for frequently queried fields
- Implement caching for stats endpoints
- Use pagination everywhere

### Risk 4: CORS Issues
**Mitigation**:
- Configure CORS properly from start
- Test with frontend early
- Document allowed origins

---

## Questions to Answer Before Starting

1. **Q**: What port should API run on?
   **A**: 5001 (Web is on 5000)

2. **Q**: Should we use Flask-RESTful or plain Flask?
   **A**: Flask-RESTful for better structure

3. **Q**: Token expiration time?
   **A**: 1 hour for access token, 7 days for refresh token

4. **Q**: Should we implement refresh tokens?
   **A**: Yes, for better UX

5. **Q**: API versioning strategy?
   **A**: URL-based (`/api/v1/`)

6. **Q**: Should existing web routes stay?
   **A**: Yes, keep both web and API

7. **Q**: Who can access API?
   **A**: Admins and external applications (with proper auth)

---

## Resources

### Documentation to Read
- Flask-RESTful: https://flask-restful.readthedocs.io/
- Flask-CORS: https://flask-cors.readthedocs.io/
- PyJWT: https://pyjwt.readthedocs.io/
- Marshmallow: https://marshmallow.readthedocs.io/

### Tools to Install
- Postman (API testing)
- Thunder Client (VS Code extension)
- DB Browser for SQLite (database inspection)

---

## Next Steps

1. Review this plan
2. Install dependencies (Phase 1.1)
3. Create directory structure (Phase 1.3)
4. Start with API app factory (Phase 2.1)
5. Implement authentication (Phase 2.3)
6. Build one complete endpoint as example (Users)
7. Test thoroughly
8. Replicate pattern for other endpoints

---

**Estimated Timeline**: 1-2 weeks for full implementation

**Priority**: Core functionality first, then documentation, then enhancements