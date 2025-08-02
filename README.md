# TodoApp Backend

A Flask-based REST API for the TodoApp application with JWT authentication, Google OAuth, and email notifications.

## Features

- **Authentication**: JWT-based authentication with email/password and Google OAuth
- **CRUD Operations**: Full CRUD for todos with user ownership
- **Email Notifications**: Automatic email notifications when todos are created
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Security**: Password hashing, input validation, and CORS protection

## Tech Stack

- **Backend**: Python 3.8+ with Flask
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **OAuth**: Google OAuth 2.0
- **Email**: Flask-Mail with SMTP
- **Deployment**: Configured for Render

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- PostgreSQL database (for production)
- Google OAuth credentials
- SMTP email account (Gmail recommended)

### 2. Installation

```bash
# Clone the repository
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the `.env` file and update with your credentials:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/todoapp

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=True

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-flask-secret-key
```

### 4. Database Setup

```bash
# Initialize the database
python init_db.py

# Or reset the database (drops all data)
python init_db.py reset
```

### 5. Running the Application

```bash
# Development mode
python run.py

# Or using Flask command
flask run
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /api/register` - Register with email/password
- `POST /api/login` - Login with email/password
- `GET /api/auth/google` - Initiate Google OAuth
- `GET /api/auth/google/callback` - Google OAuth callback
- `GET /api/verify-token` - Verify JWT token
- `GET /api/me` - Get current user info

### Todos

All todo endpoints require JWT authentication via `Authorization: Bearer <token>` header.

- `GET /api/todos` - Get all user's todos
- `POST /api/todos` - Create new todo
- `GET /api/todos/<id>` - Get specific todo
- `PUT /api/todos/<id>` - Update todo
- `DELETE /api/todos/<id>` - Delete todo
- `PUT /api/todos/bulk-update` - Bulk update todos
- `GET /api/todos/stats` - Get todo statistics

## Request/Response Examples

### Register User
```bash
POST /api/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Create Todo
```bash
POST /api/todos
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Complete project",
  "description": "Finish the TodoApp backend implementation"
}
```

### Update Todo
```bash
PUT /api/todos/1
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Updated title",
  "completed": true
}
```

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - Development: `http://localhost:5000/api/auth/google/callback`
   - Production: `https://your-domain.com/api/auth/google/callback`

## Email Configuration

For Gmail SMTP:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `MAIL_PASSWORD`

## Deployment

### Render Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set environment variables in Render dashboard
4. Deploy using the included `Procfile`

### Environment Variables for Production

Set these in your Render dashboard:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Strong secret key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `MAIL_USERNAME` - SMTP email
- `MAIL_PASSWORD` - SMTP password
- `SECRET_KEY` - Flask secret key

## Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   ├── routes/              # API routes
│   └── utils/               # Utility functions
├── config.py                # Configuration
├── run.py                   # Application entry point
├── init_db.py              # Database initialization
├── requirements.txt         # Dependencies
└── .env                    # Environment variables
```

### Testing

You can test the API using tools like:
- Postman
- curl
- Python requests
- Frontend application

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running and connection string is correct
2. **Google OAuth**: Verify redirect URIs match exactly
3. **Email**: Check SMTP credentials and app password
4. **CORS**: Frontend domain must be in CORS_ORIGINS

## Security Considerations

- Use strong JWT secret keys
- Enable HTTPS in production
- Validate all input data
- Use environment variables for secrets
- Implement rate limiting (recommended)
- Regular security updates

## License

This project is for educational purposes.
