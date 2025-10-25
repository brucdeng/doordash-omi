# User Setup Guide

## Getting Your DoorDash Drive API Credentials

### Step 1: Create DoorDash Developer Account
1. Go to [DoorDash Developer Portal](https://developer.doordash.com)
2. Sign up for a developer account using your DoorDash account
3. Navigate to the Drive section in the left sidebar
4. Note: Production access is currently limited - you'll start in Sandbox mode

### Step 2: Create an Access Key
1. In the Developer Portal, click **Credentials** in the left navigation
2. Click the **+** icon to create a new access key
3. Name your key (e.g., "OMI-Voice-App")
4. Click **Create Access Key**
5. **Copy the access key** - you'll need this for your `.env` file

### Step 3: Understanding Drive API vs Marketplace API
The app now uses **DoorDash Drive API** which is for:
- ✅ **Delivery requests** - Request deliveries from any restaurant
- ✅ **Delivery tracking** - Track delivery status
- ❌ **Restaurant search** - Not available (uses mock data)
- ❌ **Menu browsing** - Not available (uses mock data)

**Important:** Drive API is for delivery logistics, not restaurant discovery!

### Step 4: Configure Your App

1. **Copy the environment template:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your access key:**
   ```env
   DOORDASH_ACCESS_KEY=your_actual_access_key_here
   DOORDASH_BASE_URL=https://openapi.doordash.com
   
   # Optional: OpenAI for voice processing
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   python main.py
   ```

## Security Notes

- ✅ **Never share your access key**
- ✅ **Don't commit `.env` to GitHub**
- ✅ **Keep your credentials private**
- ✅ **The app works with mock data if no access key is provided**

## Testing Without Real API Keys

The app includes mock data for testing:
- Mock restaurants (Tony's Pizza Palace, etc.)
- Mock menu items (Pepperoni Pizza, etc.)
- Mock delivery responses

This lets you test the voice ordering flow without needing real DoorDash credentials!

## How Drive API Works

Based on the [DoorDash Drive API documentation](https://developer.doordash.com/en-US/docs/drive/tutorials/get_started_sdk):

1. **Create Delivery**: Request a delivery with pickup/dropoff addresses
2. **Track Delivery**: Monitor delivery status through the lifecycle
3. **Sandbox Mode**: Test without real costs or Dashers
4. **Production Access**: Limited - requires approval process

**Note:** The app uses mock restaurant/menu data since Drive API focuses on delivery logistics, not restaurant discovery.

## Troubleshooting

**App not connecting to DoorDash?**
- Check your `.env` file has correct access key
- Verify your DoorDash developer account is approved
- Check the logs for authentication errors
- Remember: Drive API is for delivery logistics, not restaurant search

**Voice commands not working?**
- Make sure you have a valid OpenAI API key
- Test with the `/test` endpoint first
