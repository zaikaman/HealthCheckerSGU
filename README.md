# 🏥 Health Checker - AI-Powered Healthcare Assistant

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20App-blue?style=for-the-badge)](https://healthcheckersgu-996c684714f1.herokuapp.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![AI Powered](https://img.shields.io/badge/AI-Google%20Gemini-orange?style=for-the-badge&logo=google)](https://ai.google.dev/)

> **A comprehensive AI-powered healthcare management platform that revolutionizes personal health monitoring and medical consultation through advanced artificial intelligence.**

## 🌟 Overview

Health Checker is an innovative web application that combines cutting-edge AI technology with practical healthcare management tools. Built with Flask and powered by Google Gemini AI, this platform provides intelligent health analysis, personalized medical consultations, and automated health reminders to help users maintain optimal wellness.

**🔗 Live Application:** [https://healthcheckersgu-996c684714f1.herokuapp.com/](https://healthcheckersgu-996c684714f1.herokuapp.com/)

## ✨ Key Features

### 🤖 AI-Powered Medical Analysis
- **Medical Document Analysis**: Upload and analyze medical records, prescriptions, and lab reports using advanced OCR and AI interpretation
- **Physical Health Assessment**: AI-powered body composition analysis through image recognition
- **Intelligent Health Insights**: Comprehensive health recommendations based on analyzed data

### 🩺 Virtual AI Doctor
- **Voice-Enabled Consultation**: Real-time voice interaction with AI medical assistant
- **Text-to-Speech Integration**: Natural conversation flow using ElevenLabs TTS technology
- **Multilingual Support**: Primarily Vietnamese with English capabilities
- **Medical Knowledge Base**: Extensive AI training for accurate health guidance

### 📅 Smart Health Management
- **Intelligent Reminders**: Automated medication, exercise, and checkup notifications
- **Flexible Scheduling**: Daily, weekly, and monthly reminder frequencies
- **Email Notifications**: Automated email alerts for important health activities
- **Timezone Awareness**: Vietnam timezone optimization for accurate scheduling

### 📊 Comprehensive Health History
- **Analysis Tracking**: Complete history of all medical document analyses
- **Health Progress Monitoring**: Track physical health assessments over time
- **Consultation Archive**: Searchable history of AI doctor interactions
- **Data Export**: Easy access to historical health data

### 🔐 Secure User Management
- **Email Verification**: Secure account creation with email confirmation
- **Password Protection**: Encrypted password storage with industry-standard hashing
- **Session Management**: Secure user sessions with JWT token authentication
- **Data Privacy**: GDPR-compliant data handling and storage

## 🛠️ Technology Stack

### Backend Architecture
- **Framework**: Flask (Python) - Lightweight and scalable web framework
- **Database**: MySQL with SQLAlchemy ORM for robust data management
- **AI Integration**: Google Gemini 2.0 Flash for advanced language processing
- **Voice Processing**: ElevenLabs API for natural text-to-speech conversion
- **Task Scheduling**: APScheduler for automated reminder system

### Cloud Infrastructure
- **Hosting**: Heroku with automatic scaling capabilities
- **File Storage**: Cloudinary for optimized image and audio storage
- **Email Service**: Gmail SMTP integration for reliable notifications
- **Database**: AWS RDS MySQL for high-availability data storage

### Frontend Technologies
- **UI Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Modern ES6+ for interactive features
- **CSS3**: Custom styling with mobile-first approach
- **Icons**: Font Awesome for professional iconography

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- MySQL database
- Google Gemini API key
- ElevenLabs API key
- Cloudinary account

### Local Development

1. **Clone the Repository**
   ```bash
   git clone https://github.com/zaikaman/health-checker.git
   cd health-checker
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Set up your environment variables
   export GEMINI_API_KEY="your_gemini_api_key"
   export ELEVENLABS_API_KEY="your_elevenlabs_api_key"
   export DATABASE_URL="your_mysql_connection_string"
   ```

4. **Database Setup**
   ```bash
   # The application will automatically create tables on first run
   python app.py
   ```

5. **Run the Application**
   ```bash
   python app.py
   # or for production
   gunicorn app:app --preload
   ```

## 📱 Usage Guide

### Getting Started
1. **Sign Up**: Create an account with email verification
2. **Login**: Access your personalized dashboard
3. **Upload Documents**: Analyze medical records and prescriptions
4. **Health Assessment**: Upload photos for AI-powered physical analysis
5. **Consult AI Doctor**: Voice or text consultation with medical AI
6. **Set Reminders**: Create automated health notifications

### API Endpoints
- `GET /` - Main dashboard
- `POST /file_analysis` - Medical document analysis
- `POST /health_analysis` - Physical health assessment
- `POST /analyze_audio` - AI doctor voice consultation
- `GET /history` - Analysis history retrieval
- `POST /reminders` - Health reminder management

## 🏗️ Project Structure

```
health-checker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment configuration
├── runtime.txt           # Python version specification
├── utils/                # Utility modules
│   ├── gemini_integration.py   # AI analysis logic
│   ├── audio_utils.py          # Audio processing
│   ├── email_utils.py          # Email functionality
│   ├── reminder_utils.py       # Scheduling system
│   └── validation_utils.py     # Input validation
├── templates/            # HTML templates
│   ├── index.html        # Main dashboard
│   ├── ai_doctor.html    # AI consultation interface
│   ├── file_analysis.html # Document analysis page
│   ├── health_analysis.html # Physical assessment page
│   └── reminders.html    # Reminder management
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Application assets
└── uploads/             # Temporary file storage
```

## 🔧 Database Schema

### Core Models
- **User**: Authentication and profile management
- **FileAnalysis**: Medical document analysis records
- **HealthAnalysis**: Physical health assessment data
- **AiDoctor**: AI consultation conversation history
- **HealthReminder**: Automated notification system

## 🌐 Deployment

The application is production-ready and deployed on Heroku with:
- Automatic SSL certificates
- Horizontal scaling capabilities
- Continuous deployment from Git
- Environment variable management
- Database connection pooling

## 🔮 Future Enhancements

- **Mobile Application**: Native iOS and Android apps
- **Wearable Integration**: Apple Watch and Fitbit connectivity
- **Advanced Analytics**: Machine learning health trend analysis
- **Telemedicine**: Video consultation capabilities
- **Multi-language Support**: Expanded language options
- **API Documentation**: OpenAPI/Swagger integration

## 👨‍💻 Developer

**Đinh Phúc Thịnh**
- 💼 **LinkedIn**: [https://www.linkedin.com/in/đinh-phúc-thịnh-2561b5274](https://www.linkedin.com/in/%C4%91inh-ph%C3%BAc-th%E1%BB%8Bnh-2561b5274)
- 🐙 **GitHub**: [https://github.com/zaikaman](https://github.com/zaikaman)
- 📧 **Email**: [zaikaman123@gmail.com](mailto:zaikaman123@gmail.com)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🙏 Acknowledgments

- Google Gemini AI for advanced language processing
- ElevenLabs for natural voice synthesis
- Cloudinary for reliable media storage
- The open-source community for amazing tools and libraries

---

<div align="center">

**Built with ❤️ for better healthcare accessibility**

*Making AI-powered healthcare available to everyone, everywhere.*

</div>