# Personalized Career Development Assistant

A powerful AI-driven application that analyzes resumes and provides personalized career development recommendations, skill suggestions, and company role matches.

![Project Banner]()

## 🌟 Features

- **Resume Analysis**: Upload your resume in PDF format for instant analysis
- **Skill Assessment**: Identifies your current technical skills and suggests improvements
- **Career Recommendations**: Provides personalized career path suggestions
- **Course Recommendations**: Suggests relevant online courses to enhance your skills
- **Company Role Matching**: Matches your profile with suitable company roles
- **Personalized To-Do Lists**: Generates actionable steps to achieve your career goals
- **Responsive Design**: Works seamlessly on both desktop and mobile devices

## 🛠️ Technologies Used

- **Frontend**: Streamlit
- **AI/ML**: 
  - LangChain
  - Google Gemini AI
  - Sentence Transformers
- **Vector Database**: Pinecone
- **Data Processing**: Pandas, PyPDF
- **Visualization**: Plotly
- **Other**: Python-dotenv, yt-dlp

## 📋 Prerequisites

- Python 3.8+
- Pinecone API Key
- Google Gemini API Key

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/personalized-career-development-assistant.git
cd personalized-career-development-assistant
```

2. Create and activate a virtual environment:
```bash
conda create -n res2_env python=3.8
conda activate res2_env
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
PINECONE_API_KEY=your_pinecone_api_key
GEMINI_API_KEY=your_gemini_api_key
```

## 💻 Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Upload your resume in PDF format

4. View your personalized career development recommendations

## 📁 Project Structure

```
personalized-career-development-assistant/
├── app.py                 # Main application file
├── requirements.txt       # Project dependencies
├── store_index.py        # Pinecone index creation and management
├── src/
│   ├── helper.py         # Helper functions
│   ├── prompt.py         # AI prompts
│   └── __init__.py
└── Data/
    └── company roles.xlsx # Company role data
```

## 🔧 Configuration

The application uses several configuration files and environment variables:

- `.env`: Contains API keys and sensitive information
- `requirements.txt`: Lists all Python dependencies
- `Data/company roles.xlsx`: Contains company role data for matching

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Yashwant K**
- GitHub: [@Yashwant00CR7](https://github.com/Yashwant00CR7)

## 🙏 Acknowledgments

- Google Gemini AI for providing the AI capabilities
- Pinecone for vector database services
- Streamlit for the web application framework

## 📸 Screenshots

### Main Interface
![Main Interface]()

### Resume Analysis
![Resume Analysis]()

### Career Recommendations
![Career Recommendations]()

### Course Suggestions
![Course Suggestions]()

## 📞 Contact

For any queries or support, please reach out to:
- GitHub Issues: [Create an issue](https://github.com/yourusername/personalized-career-development-assistant/issues)
- Email: [Your Email]

---

⭐ Star this repository if you find it helpful! 