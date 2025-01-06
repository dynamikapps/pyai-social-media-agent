# Social Media Content Generation Agent 🚀

An AI-powered tool that automatically generates platform-optimized social media posts from any website URL. Built with Python, this tool leverages FireCrawl for content extraction and GPT-4o-mini for intelligent content generation.

## 🌟 Features

- **Multi-Platform Support**

  - Twitter (X) - 280 characters
  - LinkedIn - 3,000 characters
  - Facebook - 63,206 characters
  - Instagram - 2,200 characters

- **Smart Content Generation**

  - Automatic content extraction from any URL
  - Platform-specific formatting
  - Relevant hashtag suggestions
  - SEO-optimized content
  - Call-to-action generation

- **Customization Options**

  - Target audience definition
  - Content tone adjustment
  - Custom hashtag preferences
  - Character limit monitoring

- **User Interface**
  - Clean Streamlit web interface
  - Real-time content preview
  - Character count tracking
  - Platform-specific formatting
  - One-click content generation

## 🛠️ Prerequisites

- Python 3.8 or higher
- FireCrawl API key ([Get it here](https://docs.firecrawl.dev))
- Internet connection for API access

## 📦 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/dynamikappas/pyai-social-media-agent.git
   cd pyai_social_media_agent
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp example.env .env
   ```
   Then edit `.env` with your API keys and preferences.

## 🚀 Usage

### Web Interface

1. Start the Streamlit app:

   ```bash
   streamlit run streamlit_app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter a website URL and customize your preferences

4. Click "Generate Posts" to create platform-specific content

### Command Line Interface

```bash
python -m social_media_agent <url>
```

## 📁 Project Structure

```
pyai_social_media_agent/
├── streamlit_app.py      # Web interface
├── social_media_agent.py # Core agent logic
├── requirements.txt      # Project dependencies
├── example.env          # Environment variables template
├── .env                 # Your actual environment variables
├── .gitignore          # Git ignore rules
└── outputs/            # Generated content storage
```

## ⚙️ Configuration

The following environment variables can be configured in `.env`:

- `FIRECRAWL_API_KEY` (Required): Your FireCrawl API key
- `OPENAI_API_KEY` (Optional): Custom OpenAI API key
- `LOGFIRE_TOKEN` (Optional): Logging configuration
- `DEBUG` (Optional): Enable debug mode
- `ENVIRONMENT` (Optional): Set environment (development/production)

## 🔍 Platform Character Limits

| Platform    | Character Limit |
| ----------- | --------------- |
| Twitter (X) | 280             |
| LinkedIn    | 3,000           |
| Facebook    | 63,206          |
| Instagram   | 2,200           |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FireCrawl](https://docs.firecrawl.dev) for web content extraction
- [OpenAI](https://openai.com) for GPT-4o-mini integration
- [Streamlit](https://streamlit.io) for the web interface

## 📧 Support

For support, please open an issue in the GitHub repository or contact the maintainers.
