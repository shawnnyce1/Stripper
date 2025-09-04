# Amazon Flex Grabber

A comprehensive automation tool for Amazon Flex delivery block grabbing with multi-account support, real-time monitoring, and cross-platform mobile interface.

## 🚀 Features

- **Multi-Account Support**: Manage multiple Amazon Flex accounts simultaneously
- **Automated Block Grabbing**: Intelligent bot system that monitors and accepts delivery blocks
- **Real-time Dashboard**: Live metrics, earnings tracking, and performance analytics
- **Cross-Platform Mobile App**: React Native frontend for iOS and Android
- **Docker Support**: Easy deployment with containerization
- **Secure Configuration**: Encrypted credential storage and secure API endpoints
- **Comprehensive Logging**: Detailed activity logs and error tracking

## 📋 Prerequisites

### For Local Development:
- **Python 3.11+** - Backend and automation
- **Node.js 18+** - Frontend development
- **Android Studio** - For Android emulation (optional)
- **Appium Server** - Mobile automation framework

### For Docker Deployment:
- **Docker** and **Docker Compose**

## 🛠️ Installation & Setup

### Method 1: Local Development

#### 1. Clone and Setup Backend
```bash
# Navigate to project directory
cd Amazon-Flex-Grabber

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
# Edit .env with your configuration
```

#### 2. Setup Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# For iOS (macOS only)
cd ios && pod install && cd ..
```

#### 3. Start the Application

**Backend (Terminal 1):**
```bash
# Windows
start_backend.bat

# Or manually
python backend/main.py
```

**Frontend (Terminal 2):**
```bash
# Windows
start_frontend.bat

# Or manually
cd frontend
npx expo start
```

### Method 2: Docker Deployment

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up --build

# Run in background
docker-compose -f docker/docker-compose.yml up -d --build
```

## 📱 Mobile App Setup

### Android
1. Install Expo Go from Google Play Store
2. Scan QR code from Expo development server
3. Or build APK: `npx expo build:android`

### iOS
1. Install Expo Go from App Store
2. Scan QR code from Expo development server
3. Or build IPA: `npx expo build:ios`

## 🔧 Configuration

### 1. Account Setup
- Open the mobile app
- Navigate to "Login" tab
- Add your Amazon Flex credentials
- Select preferred warehouse

### 2. Bot Configuration
- Go to "Config" tab
- Set minimum rate, max distance
- Configure auto-accept settings
- Adjust performance parameters

### 3. Environment Variables
Edit `.env` file:
```env
API_HOST=0.0.0.0
API_PORT=8000
APPIUM_HOST=localhost
APPIUM_PORT=4723
BOT_CHECK_INTERVAL=5
LOG_LEVEL=INFO
```

## 🚀 Usage

### Starting Bots
1. **Mobile App**: Home tab → Select account → Press "Start"
2. **API**: `POST /api/bot/start/{account_name}`
3. **CLI**: `python automation/multi_runner.py`

### Monitoring
- **Dashboard**: Real-time metrics and performance
- **Logs**: Check `accounts/{account_name}/logs/log.txt`
- **API**: `GET /api/metrics/summary`

## 📊 API Endpoints

### Authentication
- `POST /api/login` - Add new account
- `GET /api/accounts` - List all accounts

### Bot Management
- `POST /api/bot/start/{account_name}` - Start bot
- `POST /api/bot/stop/{account_name}` - Stop bot
- `GET /api/metrics/{account_name}` - Account metrics

### Monitoring
- `GET /api/metrics/summary` - Overall statistics
- `GET /` - Health check

## 🏗️ Architecture

```
Amazon-Flex-Grabber/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main API server
│   └── app.py              # Legacy Flask app
├── automation/             # Bot automation system
│   ├── shared/             # Shared bot modules
│   │   ├── bot_core.py     # Core bot logic
│   │   ├── appium_setup.py # Mobile automation
│   │   └── utils.py        # Utility functions
│   └── multi_runner.py     # Multi-account runner
├── frontend/               # React Native mobile app
│   ├── screens/            # App screens
│   ├── App.js              # Main app component
│   └── package.json        # Dependencies
├── accounts/               # Account configurations
│   └── {account_name}/     # Individual account data
│       ├── config.json     # Account settings
│       ├── .env            # Credentials
│       └── logs/           # Activity logs
├── docker/                 # Docker configuration
│   ├── docker-compose.yml  # Multi-service setup
│   ├── Dockerfile.backend  # Backend container
│   └── Dockerfile.bot      # Bot container
└── app/                    # Android app source
```

## 🔒 Security Features

- **Encrypted Passwords**: Credentials stored securely
- **API Authentication**: Secure endpoint access
- **Local Storage**: No cloud data transmission
- **Environment Isolation**: Separate account configurations

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Frontend build errors:**
```bash
# Clear cache
npx expo r -c

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Appium connection issues:**
```bash
# Check Appium server
appium doctor

# Start Appium manually
appium server --address 0.0.0.0 --port 4723
```

### Logs Location
- **Backend**: Console output
- **Bot Activity**: `accounts/{account_name}/logs/log.txt`
- **Frontend**: Expo development console

## 📈 Performance Tips

1. **Optimize Check Interval**: Balance between speed and resource usage
2. **Multiple Accounts**: Run bots for different warehouses
3. **Resource Monitoring**: Monitor CPU and memory usage
4. **Network Stability**: Ensure stable internet connection

## ⚖️ Legal Disclaimer

This tool is for educational purposes only. Users are responsible for:
- Complying with Amazon Flex Terms of Service
- Following local laws and regulations
- Using the tool ethically and responsibly

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: GitHub Issues tab
- **Documentation**: Check README and code comments
- **Community**: Discussions tab for questions

---

**⚠️ Important**: Always ensure compliance with Amazon Flex Terms of Service and local regulations when using this tool.