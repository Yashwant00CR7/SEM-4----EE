# Personalized Career Development Assistant

An AI-driven application that analyzes resumes and provides personalized career recommendations, skill suggestions, and company role matches using RAG and Gemini AI.

![Project Banner](https://github.com/user-attachments/assets/81cbc7b2-629c-4330-9a8b-7d9420aabff3)

**[Try it live →](https://personalized-career-development-bot.streamlit.app/)**

---

## 🌟 Features

- **Resume Analysis**: Upload your resume in PDF format for instant analysis
- **Skill Assessment**: Identifies current technical skills and suggests improvements
- **Career Recommendations**: Personalized career path suggestions based on your profile
- **Course Recommendations**: Relevant online courses to fill skill gaps
- **Company Role Matching**: Matches your profile with suitable company roles using vector similarity
- **Personalized To-Do Lists**: Actionable steps to achieve your career goals
- **Responsive Design**: Works on desktop and mobile

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: LangChain, Google Gemini AI, Sentence Transformers
- **Vector Database**: Pinecone
- **Data Processing**: Pandas, PyPDF, Plotly

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Pinecone API Key
- Google Gemini API Key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Yashwant00CR7/Personalized-Suggestion-AI.git
cd Personalized-Suggestion-AI
```

2. Create and activate a virtual environment:
```bash
conda create -n res2_env python=3.8
conda activate res2_env
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
PINECONE_API_KEY=your_pinecone_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## 💻 Usage

```bash
streamlit run store_index.py  # First time only — builds Pinecone index
streamlit run app.py
```

Open `http://localhost:8501`, upload your resume PDF, and get your personalized roadmap.

---

## 📁 Project Structure

```
├── app.py                 # Main application
├── store_index.py         # Pinecone index creation
├── requirements.txt
├── src/
│   ├── helper.py
│   ├── prompt.py
│   └── __init__.py
└── Data/
    └── company roles.xlsx
```

---

## 📸 Screenshots

### Main Interface
![Resume Analysis](https://github.com/user-attachments/assets/117b12ac-15a8-475b-882c-4ccc806e36f5)

### Career Recommendations
![Career Recommendations](https://github.com/user-attachments/assets/5fed0af6-e154-4839-9897-09a3d5195004)

### Course Suggestions
![Course Suggestions](https://github.com/user-attachments/assets/6646a9ad-18b1-41f9-b30d-b3add8c021fb)

---

## 👨‍💻 Author

**Yashwant K** · [GitHub](https://github.com/Yashwant00CR7) · [LinkedIn](https://www.linkedin.com/in/yashwant-k-935aa0292/)

## 📝 License

MIT License
