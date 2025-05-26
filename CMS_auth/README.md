# CMS Authentication System

A robust Content Management System (CMS) authentication system built with Flask, featuring secure user management, AWS S3 integration, and PostgreSQL database.

## Features

- Secure user authentication and authorization
- PostgreSQL database integration
- AWS S3 file storage
- Flask-Login for session management
- Database migrations using Flask-Migrate
- Form validation and CSRF protection
- Secure password hashing
- Logging system for debugging
- Production-ready with Gunicorn support

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Git
- AWS account with S3 access
- pip (Python package installer)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CMS_auth
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

1. Install PostgreSQL if not already installed
   - [PostgreSQL Downloads](https://www.postgresql.org/download/)

2. Create a new PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE your_database_name;
```

### 5. Environment Configuration

1. Create a `.env` file in the project root:
```bash
cp env.example .env
```

2. Update the `.env` file with your configurations:
```plaintext
# Application settings
FLASK_APP=main.py
FLASK_ENV=development  # Change to production in production environment

# Security
SECRET_KEY=your-secure-secret-key
WTF_CSRF_SECRET_KEY=your-secure-csrf-key

# Database connection
DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=your-aws-region
S3_BUCKET_NAME=your-s3-bucket-name

# File uploads
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

### 6. Generate Security Keys

Run the provided script to generate secure keys:
```bash
python generate_keys.py
```

Copy the generated keys to your `.env` file.

### 7. Database Migration

Initialize and apply database migrations:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 8. Create Admin User

Run the script to create your first admin user:
```bash
python create_new_user.py
```

### 9. Run the Application

Start the development server:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## AWS S3 Setup

1. Create an AWS account if you don't have one
2. Create a new S3 bucket:
   - Go to AWS Console → S3
   - Click "Create bucket"
   - Choose a unique bucket name
   - Configure bucket settings (enable versioning if needed)
   - Set appropriate permissions

3. Create IAM User:
   - Go to AWS Console → IAM
   - Create a new user with programmatic access
   - Attach AmazonS3FullAccess policy (or create a custom policy with limited scope)
   - Save the Access Key ID and Secret Access Key

4. Update your `.env` file with the AWS credentials

## Production Deployment

For production deployment:

1. Update environment variables:
```plaintext
FLASK_ENV=production
```

2. Set up Gunicorn:
```bash
gunicorn -c gunicorn.conf.py main:app
```

3. Configure your web server (Nginx/Apache) to proxy requests to Gunicorn

## Database Maintenance

### Backup Database
```bash
pg_dump -U username -d database_name > backup.sql
```

### Restore Database
```bash
psql -U username -d database_name < backup.sql
```

### Run Database Migrations
```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migrations
flask db downgrade
```

## Troubleshooting

- Check `flask_debug.log` and `error.log` for detailed error messages
- Ensure all environment variables are properly set
- Verify database connection string
- Check AWS credentials and S3 bucket permissions
- Ensure proper file permissions on uploaded content

## Security Notes

- Always use HTTPS in production
- Regularly update dependencies
- Keep your secret keys secure and never commit them to version control
- Regularly backup your database
- Monitor application logs for suspicious activities
- Use strong passwords for admin accounts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Information] 