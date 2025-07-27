# ainalyzit - AI Food Analysis Platform

An AI-powered food analysis application that uses Google's Gemini Vision API to analyze food ingredients and provide health insights.

## Features

- 📸 **Image Analysis**: Upload food packaging or ingredient lists for AI analysis
- 🧬 **Health Scoring**: Get detailed health scores and Nutri-Scores
- 🌱 **Eco-Scoring**: Environmental impact assessment
- 📊 **Interactive Charts**: Visual representation of nutritional data
- 🔄 **Alternatives**: Healthier product recommendations
- 📱 **Responsive Design**: Works on all devices

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ainalyzit
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Required environment variables:
- `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `SECRET_KEY`: Generate a secure Django secret key
- `MONGO_USER`, `MONGO_PASS`, `MONGO_CLUSTER_URL`: MongoDB Atlas credentials
- `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`: Auth0 configuration

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional
```

### 6. Run the Application
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## API Keys Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### MongoDB Atlas
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Create a database user
4. Get your connection string and update `.env`

### Auth0 (Optional)
1. Create an account at [Auth0](https://auth0.com/)
2. Create a new application
3. Configure your domain and credentials in `.env`

## Project Structure

```
ainalyzit/
├── ainalyzit/          # Main Django app
├── analysis/           # Food analysis logic
├── api/               # API endpoints
├── dashboard/         # Dashboard views
├── users/             # User management
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── media/            # Uploaded files
```

## Security Notes

- Never commit your `.env` file to version control
- Use strong, unique secret keys in production
- Keep your API keys secure and rotate them regularly
- Enable proper authentication and authorization for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
