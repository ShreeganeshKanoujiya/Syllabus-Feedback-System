# Syllabus Feedback System

## Overview
A web-based system designed to collect, manage, and analyze feedback on course syllabi from multiple stakeholders (students, faculty, alumni, parents, and industry representatives).

## Features
- Submit structured feedback on syllabi from different stakeholder perspectives
- Secure admin dashboard for feedback management
- Multiple feedback forms for different user categories
- Feedback history and data management
- Database-driven architecture with MySQL
- RESTful API endpoints

### Prerequisites
- Python 3.11 or higher
- uv (Python package manager and runtime)
- MySQL database

### Installation
```bash
git clone <repository-url>
cd Syllabus-Feedback-System
uv sync
```

### Database Setup
```bash
# Run the database setup script
mysql -u your_user -p your_database < setup_database.sql
```

### Usage
```bash
uv fastapi dev app/main.py
```

The application will start on `http://localhost:8000`

## Project Structure
```
├── app/
│   ├── main.py                 # Application entry point
│   ├── database.py             # Database connection
│   ├── models.py               # Data models
│   ├── routes/
│   │   ├── admin.py           # Admin routes
│   │   └── client.py          # Client feedback routes
│   ├── templates/             # HTML templates
│   │   └── feedbackForms/    # Stakeholder-specific forms
│   └── static/                # CSS, JS, images
├── pyproject.toml             # Project configuration
├── setup_database.sql         # Database initialization script
└── README.md
```


## Getting Started
How to setup 
**Step1:** pip install uv<br>
**Step2:** Clone repo<br>
**Step3:** cd dir to syllabus-feedback-system<br>
**Step4:** Run on terminal "uv sync"<br>
**Step5:** Run database_setup.sql script in MySQL<br>
**Step6:** Change credentials in .env file according to your Mysql credentials <br>
**Step7:** Run on terminal "uv run fastapi dev app/main.py"<br>
**Step8:** Open and change username or password in create_admin.py<br>
**Step9:** Run create_admin.py file

## Contributing
Contributions are welcome. Please submit a pull request with a clear description of changes.

## License
MIT

## Contact
For questions or support, please open an issue in the repository.