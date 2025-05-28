# SAP ABAP Job Search Application

A secure web application that searches for SAP ABAP job opportunities with corp-to-corp (C2C) arrangements using Perplexity AI.

## 🔒 Security Features

- **Input Sanitization**: All user inputs and API responses are sanitized to prevent XSS attacks
- **URL Validation**: All links are validated before display
- **Environment Variables**: API keys stored securely in environment files
- **Error Handling**: Generic error messages to prevent information disclosure
- **Production Settings**: Debug mode disabled by default

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd sap-abap-job-search
```

### 2. Configure API Key
```bash
# Copy the example config file
cp config.env.example config.env

# Edit config.env and add your Perplexity API key
# PERPLEXITY_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies
```bash
pip install flask requests tabulate
```

### 4. Run the Application
```bash
python web_app.py
```

### 5. Access the App
Open your browser and go to: `http://localhost:5000`

## 📁 File Structure

```
├── web_app.py              # Main Flask application
├── index.html              # Frontend interface
├── job_search.py           # Command-line version
├── config.env.example      # Template for API configuration
├── config.env              # Your actual API configuration (gitignored)
├── .gitignore              # Prevents sensitive files from being committed
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `config.env` file with:

```env
PERPLEXITY_API_KEY=your_api_key_here
PERPLEXITY_API_URL=https://api.perplexity.ai/chat/completions
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online
```

### Production Deployment

For production deployment:

1. Set `FLASK_DEBUG=False` environment variable
2. Use a proper WSGI server like Gunicorn
3. Set up HTTPS with SSL certificates
4. Configure firewall rules
5. Use environment variables instead of config files

```bash
# Production example
export FLASK_DEBUG=False
export PERPLEXITY_API_KEY=your_key_here
gunicorn -w 4 -b 0.0.0.0:8000 web_app:app
```

## 🛡️ Security Best Practices

### API Key Security
- ✅ API keys stored in environment files
- ✅ Config files are gitignored
- ✅ Example config provided without real keys

### Input Validation
- ✅ All text inputs are HTML-escaped
- ✅ URLs are validated before use
- ✅ API responses are sanitized

### Error Handling
- ✅ Generic error messages in production
- ✅ Detailed errors only in debug mode
- ✅ No sensitive information in error responses

### Frontend Security
- ✅ XSS prevention with textContent instead of innerHTML
- ✅ URL validation before creating links
- ✅ Safe DOM manipulation

## 🔍 Features

- **Real-time Job Search**: Uses Perplexity AI to find current job openings
- **C2C Focus**: Specifically searches for corp-to-corp arrangements
- **Visa-Friendly**: Filters for positions open to visa holders
- **Clean Interface**: Modern, responsive web design
- **Link Validation**: Ensures job application links are working
- **Statistics Dashboard**: Shows job counts and metrics

## 🐛 Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify your API key in `config.env`
   - Check if the key has sufficient credits
   - Ensure no extra spaces in the config file

2. **No Jobs Found**
   - API might be rate-limited
   - Try again after a few minutes
   - Check your internet connection

3. **Links Not Working**
   - Some job boards use dynamic links
   - Use the job title to search manually
   - Check the debug section for source URLs

### Debug Mode

To enable debug mode for troubleshooting:

```bash
export FLASK_DEBUG=True
python web_app.py
```

**⚠️ Never use debug mode in production!**

## 📝 License

This project is for educational and personal use only. Please respect the terms of service of job boards and APIs used.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This application searches for publicly available job postings. Always verify job details and company legitimacy before applying. The authors are not responsible for the accuracy of job information or the legitimacy of job postings. 