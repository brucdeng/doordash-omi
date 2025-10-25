# OMI DoorDash Ordering App

Voice-activated food delivery ordering with OMI devices. Order food by voice using natural language commands like "Order a pepperoni pizza from the closest highly rated place."

## 🎯 Features

- **Voice-Activated Ordering**: Use natural language to order food
- **AI-Powered Processing**: Intelligent food item and restaurant matching
- **Restaurant Search**: Find the best restaurants based on your preferences
- **Order Management**: Track orders and manage order history
- **User Preferences**: Save delivery addresses, dietary restrictions, and favorites
- **Quick Re-ordering**: Re-order your usual or recent orders
- **Real-time Updates**: Track order status and delivery progress

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- DoorDash API access (for production)
- OpenAI API key (for AI processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd omi-doordash-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Visit the app**
   - Homepage: `http://localhost:8000/`
   - Test interface: `http://localhost:8000/test`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# DoorDash API Configuration
DOORDASH_API_KEY=your_doordash_api_key_here
DOORDASH_CLIENT_ID=your_doordash_client_id_here
DOORDASH_CLIENT_SECRET=your_doordash_client_secret_here
DOORDASH_BASE_URL=https://openapi.doordash.com

# OpenAI API Key (for AI voice processing)
OPENAI_API_KEY=your_openai_api_key_here

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000
```

### DoorDash API Setup

1. **Get DoorDash API Access**
   - Visit [DoorDash Developer Portal](https://developer.doordash.com/)
   - Create an account and request API access
   - Get your API key and credentials

2. **Configure API Keys**
   - Add your DoorDash API credentials to `.env`
   - For testing, the app includes mock data

### OpenAI Setup

1. **Get OpenAI API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Create an API key
   - Add to your `.env` file

## 📱 Usage

### Voice Commands

The app supports natural language voice commands:

**Basic Orders:**
- "Order a pepperoni pizza from the closest highly rated place"
- "Get me a burger from the nearest restaurant"
- "I want Chinese food delivered"

**Advanced Orders:**
- "Order my usual from Tony's Pizza"
- "Get a gluten-free pizza from the closest place"
- "I'm hungry, order something healthy nearby"

### Web Interface

1. **Homepage** (`/`): Main interface with quick actions
2. **Test Interface** (`/test`): Test voice commands and see processing
3. **Order Management**: View and manage your orders

## 🏗️ Architecture

### Core Components

- **`main.py`**: FastAPI application with mobile-first UI
- **`doordash_client.py`**: DoorDash API integration
- **`voice_processor.py`**: AI-powered voice command processing
- **`order_manager.py`**: Order storage and tracking
- **`user_preferences.py`**: User preferences and order history

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Homepage with order management |
| `/test` | GET | Voice command testing interface |
| `/webhook` | POST | OMI device voice command processor |
| `/confirm-order` | POST | Confirm and place order |
| `/order-status/{order_id}` | GET | Get order status |
| `/set-preferences` | POST | Update user preferences |
| `/user-preferences/{user_id}` | GET | Get user preferences |
| `/order-history/{user_id}` | GET | Get order history |
| `/health` | GET | Health check |

## 🚀 Deployment

### Railway Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Select your repository
   - Add environment variables in Railway dashboard

3. **Configure OMI Device**
   - Set webhook URL: `https://your-app.up.railway.app/webhook`
   - Enable the integration in OMI settings

### Environment Variables for Railway

```
DOORDASH_API_KEY=your_doordash_api_key
DOORDASH_CLIENT_ID=your_doordash_client_id
DOORDASH_CLIENT_SECRET=your_doordash_client_secret
OPENAI_API_KEY=your_openai_key
APP_HOST=0.0.0.0
APP_PORT=8000
PYTHONUNBUFFERED=1
```

## 🧪 Testing

### Voice Command Testing

1. **Visit Test Interface**: `http://localhost:8000/test`
2. **Try Example Commands**:
   - "Order a pepperoni pizza from the closest highly rated place"
   - "Get me a burger from the nearest restaurant"
   - "I want Chinese food delivered"

3. **Test Order Flow**:
   - Voice command → Intent extraction → Restaurant search → Menu items → Order confirmation

### Mock Data

The app includes mock data for testing without API keys:
- Mock restaurants with ratings and delivery times
- Mock menu items with prices and dietary info
- Mock order processing and confirmation

## 🔐 Security

- **API Key Security**: Keys stored in environment variables
- **User Data**: File-based storage with JSON persistence
- **HTTPS**: Enforced in production deployments
- **Input Validation**: Pydantic models for request validation

## 📊 Features

### Voice Processing
- **Intent Extraction**: AI-powered understanding of voice commands
- **Food Item Matching**: Smart matching of spoken items to menu items
- **Dietary Restrictions**: Support for vegetarian, vegan, gluten-free, etc.
- **Location Preferences**: "Closest" and "nearby" restaurant selection

### Order Management
- **Order Tracking**: Real-time order status updates
- **Order History**: Complete order history with re-ordering
- **User Preferences**: Delivery addresses, dietary restrictions, favorites
- **Quick Re-ordering**: "Order my usual" functionality

### Restaurant Search
- **Smart Matching**: AI-powered restaurant recommendations
- **Rating-based Selection**: Prioritize highly-rated restaurants
- **Dietary Filtering**: Filter restaurants by dietary requirements
- **Location-based**: Find closest or nearby restaurants

## 🐛 Troubleshooting

### Common Issues

1. **"No restaurants found"**
   - Check DoorDash API credentials
   - Verify location data
   - Try different search terms

2. **"Voice command not understood"**
   - Use clearer, more specific commands
   - Check OpenAI API key
   - Try example commands from test interface

3. **"Order not placing"**
   - Verify delivery address is set
   - Check DoorDash API status
   - Ensure restaurant is open

### Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **DoorDash API**: [developer.doordash.com](https://developer.doordash.com/)
- **OpenAI API**: [platform.openai.com](https://platform.openai.com/)
- **OMI Documentation**: [docs.omi.me](https://docs.omi.me/)

## 🎉 Credits

Built for the OMI ecosystem with:
- **OMI Team** - Amazing wearable AI platform
- **DoorDash** - Food delivery platform
- **OpenAI** - Intelligent voice processing

---

**Made with ❤️ for voice-first food delivery**

**Key Features:**
- 🎤 Voice-activated food ordering
- 🧠 AI-powered restaurant and menu matching
- 📱 Mobile-first order management
- 🔐 Secure API integration
- ⚡ Real-time order tracking
