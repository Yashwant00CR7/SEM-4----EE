# SET UP:
# conda activate res2_env

# 1. INSTALL BELOW LIBRARIES
"""
pip install -r requirements.txt
pip install streamlit
pip install pymysql
pip install pandas
pip install plotly
pip install PyPDF2
pip install python-dotenv
pip install langchain-google-genai
"""

# 2. CREATE FOLDER STRUCTURE AND FILES AS BEFORE
import json
from PIL import Image
import streamlit as st
import pandas as pd
import base64, random
import time, datetime
from pypdf import PdfReader
import io, os
from src.helper import download_hugging_face_embeddings
from src.prompt import *
from streamlit_tags import st_tags
import plotly.express as px
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# === Set Pinecone & Gemini API keys ===
os.environ["PINECONE_API_KEY"] = os.environ.get('PINECONE_API_KEY')
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# === Initialize Pinecone for Company Roles ===
embeddings = download_hugging_face_embeddings()
index_name = "domain-decoders"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

def fetch_yt_video(link):
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(link, download=False)
        return info.get('title', 'Unknown Title')

def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def extract_resume_data(pdf_path):
    try:
        # Read PDF text
        reader = PdfReader(pdf_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])

        # Create structured prompt
        prompt = f"""
        Analyze this resume and extract information in STRICT JSON FORMAT:
        {{
            "name": "Full name",
            "email": "Email address",
            "phone": "Phone number",
            "skills": ["list", "of", "technical", "skills"],
            "experience_level": "Fresher/Intermediate/Experienced",
            "education": ["Education entries"],
            "projects": ["Project descriptions"]
        }}

        Rules:
        1. Phone format: +XX-XXXXXXXXXX
        2. Skills must be technical terms
        3. Experience level based on work duration
        4. Return empty values if not found

        Resume Content:
        {text[:10000]}
        """

        # Get Gemini response
        response = llm.invoke(prompt)
        
        # Clean and parse JSON
        json_str = response.content.strip()
        json_str = json_str.replace('```json', '').replace('```', '')
        data = json.loads(json_str)

        # Validate required fields
        required_fields = ["name", "email", "skills"]
        for field in required_fields:
            if field not in data or not data[field]:
                st.error(f"Missing required field: {field}")
                data[field] = "" if field != "skills" else []

        return data

    except Exception as e:
        st.error(f"Resume parsing failed: {str(e)}")
        return {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience_level": "Fresher",
            "education": [],
            "projects": []
        }
    
def skill_recommender(current_skills):
    try:
        prompt = f"""
        Recommend 18 most important technical skills to add to these existing skills: {', '.join(current_skills)}.
        Focus on in-demand skills for software development roles.
        Return only a comma-separated list, no other text.
        """
        response = llm.invoke(prompt)
        return [skill.strip() for skill in response.content.split(",")]
    except Exception as e:
        st.error(f"Recommendation error: {str(e)}")
        return []

def course_recommender(skills):
    try:
        prompt = f"""
        Recommend 8 relevant online courses for someone with these skills: {', '.join(skills)}.
        Respond in this EXACT format for each course:
        "Course Title | Description (15 words) | URL | Category (Programming/Data Science/Web Dev/Design/Business)"
        
        Example:
        "Python Crash Course | Learn Python fundamentals through hands-on projects | https://example.com | Programming"
        
        Return only the 8 course entries line by line, no additional text.
        """
        response = llm.invoke(prompt)
        
        # Process response
        courses = []
        for line in response.content.split("\n"):
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 4:
                    # Always use a static placeholder image with the category as text
                    thumbnail = f"https://placehold.co/400x240?text={parts[3].replace(' ', '+')}"
                    courses.append({
                        "title": parts[0],
                        "description": parts[1],
                        "url": parts[2],
                        "category": parts[3],
                        "thumbnail": thumbnail
                    })
        return courses[:5]
        
    except Exception as e:
        st.error(f"Course recommendation error: {str(e)}")
        return []

def insert_data(*args, **kwargs):
    pass

st.set_page_config(page_title="AI Resume Analyzer", page_icon='📄', layout="wide")

def inject_custom_css():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        html, body, .main {
            height: 100%;
            min-height: 100vh;
            font-family: 'Poppins', sans-serif !important;
            background: linear-gradient(135deg, #f8cdda 0%, #1fa2ff 100%, #a1c4fd 100%);
            background-attachment: fixed;
        }
        .main {
            background: none !important;
            padding: 1rem;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        h1 {
            font-size: clamp(1.8rem, 4vw, 2.8rem);
            color: #22223b;
            margin-bottom: 1.5rem;
        }
        h2 {
            font-size: clamp(1.6rem, 3vw, 2.2rem);
            color: #22223b;
        }
        h3 {
            font-size: clamp(1.4rem, 2.5vw, 1.6rem);
            color: #22223b;
        }
        .card {
            border-radius: 24px;
            padding: clamp(1.5rem, 3vw, 2.5rem) clamp(1rem, 2vw, 2rem);
            background: rgba(255, 255, 255, 0.25);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1.5px solid rgba(255, 255, 255, 0.35);
            margin: clamp(1rem, 2vw, 2rem) 0;
            transition: box-shadow 0.3s, transform 0.3s;
            width: 100%;
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }
        .card:hover {
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25);
            transform: translateY(-4px) scale(1.01);
        }
        .skill-chip {
            display: inline-block;
            background: rgba(255,255,255,0.45);
            padding: clamp(0.8rem, 1.5vw, 1.4rem) clamp(1.4rem, 2.8vw, 2.8rem);
            border-radius: 30px;
            margin: 0.5rem;
            color: #22223b;
            font-weight: 600;
            font-size: clamp(0.9rem, 1.5vw, 1.1rem);
            box-shadow: 0 2px 8px rgba(31, 38, 135, 0.08);
            border: 1px solid rgba(255,255,255,0.3);
        }
        .course-card {
            background: rgba(255,255,255,0.30);
            border-radius: 20px;
            padding: clamp(1rem, 2vw, 2rem) clamp(0.8rem, 1.5vw, 1.5rem);
            margin: clamp(1rem, 2vw, 2rem) 0;
            box-shadow: 0 6px 24px 0 rgba(31, 38, 135, 0.13);
            transition: box-shadow 0.3s, transform 0.3s;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            align-items: flex-start;
            border: 1.5px solid rgba(255,255,255,0.25);
            backdrop-filter: blur(10px);
            width: 100%;
        }
        @media (min-width: 768px) {
            .course-card {
                flex-direction: row;
                align-items: center;
            }
        }
        .course-card:hover {
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.22);
            transform: translateY(-4px) scale(1.01);
        }
        .edu-proj-item {
            display: flex;
            align-items: flex-start;
            background: rgba(255,255,255,0.35);
            border-radius: 16px;
            margin: 1.2rem 0;
            padding: 1.2rem 1.5rem;
            box-shadow: 0 4px 18px 0 rgba(31, 38, 135, 0.10);
            border-left: 8px solid;
            border-image: linear-gradient(135deg, #f8cdda 0%, #1fa2ff 100%, #a1c4fd 100%) 1;
            transition: box-shadow 0.3s, transform 0.3s;
            width: 100%;
        }
        .edu-proj-title {
            font-size: clamp(1rem, 1.5vw, 1.22rem);
            font-weight: 700;
            color: #22223b;
            margin-bottom: 0.3rem;
            letter-spacing: 0.2px;
        }
        .edu-proj-detail {
            font-size: clamp(0.9rem, 1.2vw, 1.08rem);
            color: #4a6fa5;
            font-weight: 500;
            margin-left: 0.1rem;
        }
        .personal-info h4 {
            font-size: clamp(1.2rem, 1.8vw, 1.5rem);
            margin: 1.2rem 0;
            color: #22223b;
        }
        .personal-info p {
            color: #4a6fa5;
            margin: 0.5rem 0;
            font-size: clamp(0.9rem, 1.2vw, 1.1rem);
        }
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
            width: 100%;
        }
        .details-section {
            text-align: center;
            padding: 1rem;
        }
        .education-list, .project-list {
            text-align: left;
            margin: 0 auto;
            width: 100%;
        }
        .stButton>button {
            background: linear-gradient(90deg, #a1c4fd 0%, #c2e9fb 100%);
            color: #22223b;
            border-radius: 10px;
            padding: clamp(0.8rem, 1.5vw, 1rem) clamp(1.4rem, 2.8vw, 2.8rem);
            font-weight: 600;
            font-size: clamp(0.9rem, 1.2vw, 1.1rem);
            border: none;
            box-shadow: 0 2px 8px rgba(31, 38, 135, 0.08);
            transition: background 0.3s, color 0.3s, box-shadow 0.3s;
            width: 100%;
            max-width: 300px;
            margin: 0 auto;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #f8cdda 0%, #a1c4fd 100%);
            color: #22223b;
            box-shadow: 0 4px 16px rgba(31, 38, 135, 0.13);
        }
        .sidebar .sidebar-content {
            background: rgba(255,255,255,0.10);
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            background: rgba(161,196,253,0.15);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(31,38,135,0.13);
            border-radius: 8px;
        }
        /* Responsive images */
        img {
            max-width: 100%;
            height: auto;
        }
        /* Responsive columns */
        @media (max-width: 768px) {
            .stColumns {
                flex-direction: column;
            }
            .stColumn {
                width: 100% !important;
                margin: 1rem 0;
            }
        }
        /* File uploader styling */
        .stFileUploader {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
        }
        /* Container padding */
        .stContainer {
            padding: 1rem;
        }
        /* Responsive text */
        p, span, div {
            font-size: clamp(0.9rem, 1.2vw, 1.1rem);
        }
    </style>
    """, unsafe_allow_html=True)

def get_company_role_recommendations(skills, top_k=5):
    """
    Given a list of user skills, retrieve the most relevant company roles from Pinecone.
    """
    try:
        # Prepare the query string from user skills
        query = ", ".join(skills)
        if not query.strip():
            st.warning("No skills provided for company role recommendations.")
            return []

        # Retrieve relevant documents from Pinecone
        docs = retriever.get_relevant_documents(query)
        if not docs:
            st.warning("No relevant company roles found in the database.")
            return []

        # Parse and format the results
        roles = []
        for doc in docs[:top_k]:
            # Each doc.page_content is a string with company role info
            # Example format: "Company: ...\nRole: ...\nResponsibilities: ...\n..."
            lines = doc.page_content.split('\n')
            role_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    role_info[key.strip()] = value.strip()
            # Only add if essential fields are present
            if "Company" in role_info and "Role" in role_info:
                roles.append({
                    "company": role_info.get("Company", ""),
                    "role": role_info.get("Role", ""),
                    "responsibilities": role_info.get("Responsibilities", ""),
                    "language": role_info.get("Language", ""),
                    "knowledge": role_info.get("Essential Knowledge", ""),
                    "experience": role_info.get("Experience Required", ""),
                    "level": role_info.get("Level of Role", ""),
                    "package": role_info.get("Package Details", ""),
                })
        return roles
    except Exception as e:
        st.error(f"Error getting company role recommendations: {str(e)}")
        return []

def generate_todo_list_for_role(user_skills, role):
    """
    Use Gemini LLM to generate a personalized to-do list for the user to attain the given role.
    """
    prompt = f"""
    The user has these skills: {', '.join(user_skills)}.
    The target company role is:
    Company: {role['company']}
    Role: {role['role']}
    Responsibilities: {role['responsibilities']}
    Language: {role['language']}
    Essential Knowledge: {role['knowledge']}
    Experience Required: {role['experience']}
    Level: {role['level']}
    Package: {role['package']}
    
    Please provide a step-by-step, actionable to-do list (5-7 items) for the user to become a strong candidate for this role. 
    Focus on skills to learn, certifications, projects, networking, and other career moves. 
    Format as a numbered list.
    """
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Could not generate to-do list: {str(e)}"

def run():
    inject_custom_css()
    
    # Main header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1>Personalized Career Development Assistant</h1>
        <p style="font-size: 1.2rem; color: #4a6fa5;">Get instant career recommendations based on your resume</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## Navigation")
        activities = ["User Portal"]
        choice = st.selectbox("Choose Section:", activities)
        st.markdown("---")
        st.markdown("""
        <div style="margin-top: 3rem; color: #4a6fa5; font-size: 1rem; text-align: center;">
            <p style="font-weight: 600;">Developed by Yashwant K</p>
            <a href="https://github.com/Yashwant00CR7/" 
               style="color: #1e3d59; text-decoration: none;">
                GitHub Repository
            </a>
        </div><
        """, unsafe_allow_html=True)

    if choice == "User Portal":
        with st.container():
            st.markdown("""<div style="text-align:center;">
    <h2 style="font-size:2.3rem; margin-bottom:2rem;">Upload Your Resume</h2>
    </div>""",unsafe_allow_html=True)
            pdf_file = st.file_uploader("", type=["pdf"], help="Upload your resume in PDF format")
            st.markdown('<center><div style="mix-width: 1200px; margin: 0 auto;justify-content: center;"></center>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)
            
            if pdf_file:
                save_path = f"./Uploaded_Resumes/{pdf_file.name}"
                with open(save_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                
                with st.spinner('Analyzing Resume...'):
                    resume_data = extract_resume_data(save_path)
                    page_count = len(PdfReader(save_path).pages)
                    exp_level = resume_data.get('experience_level', 'Fresher')
                    current_skills = resume_data.get('skills', [])
                    recommended_skills = skill_recommender(current_skills)
                    recommended_courses = course_recommender(current_skills)
                    
                    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                
                st.markdown("---")
                # st.markdown("## Analysis Report")

                # Prepare Education and Projects HTML
                education_html = ""
                if resume_data.get('education'):
                    education_html = (
                        '<div class="details-section" style="grid-column: 1 / -1; margin-bottom: 2.5rem;">'
                        '<h4 style="color: #1e3d59; font-size: 1.25rem; font-weight: 600; margin-bottom: 1.2rem; text-align:left;">🎓 Education</h4>'
                        '<div class="education-list">'
                        + ''.join([
                            f'<div style="background: #f8f9fa; border-radius: 12px; box-shadow: 0 2px 8px rgba(31,38,135,0.07); padding: 1.1rem 1.5rem; margin-bottom: 1.1rem; border-left: 5px solid #a1c4fd;">'
                            f'<span style="font-size: 1.08rem; font-weight: 600; color: #22223b;">{edu.split("|", 1)[0]}</span>'
                            f'<br><span style="font-size: 1.02rem; color: #4a6fa5; font-weight: 500;">{edu.split("|", 1)[1] if "|" in edu else ""}</span>'
                            f'</div>'
                            for edu in resume_data.get('education', ['No education details found'])
                        ]) +
                        '</div></div>'
                    )
                
                projects_html = ""
                if resume_data.get('projects'):
                    projects_html = (
                        '<div class="details-section" style="grid-column: 1 / -1; margin-bottom: 2.5rem;">'
                        '<h4 style="color: #1e3d59; font-size: 1.25rem; font-weight: 600; margin-bottom: 1.2rem; text-align:left;">🔧 Key Projects</h4>'
                        '<div class="project-list">'
                        + ''.join([
                            f'<div style="background: #f8f9fa; border-radius: 12px; box-shadow: 0 2px 8px rgba(31,38,135,0.07); padding: 1.1rem 1.5rem; margin-bottom: 1.1rem; border-left: 5px solid #f8cdda;">'
                            f'<span style="font-size: 1.08rem; font-weight: 600; color: #22223b;">{project.split("|", 1)[0]}</span>'
                            f'<br><span style="font-size: 1.02rem; color: #4a6fa5; font-weight: 500;">{project.split("|", 1)[1] if "|" in project else ""}</span>'
                            f'</div>'
                            for project in resume_data.get('projects', ['No project details found'])
                        ]) +
                        '</div></div>'
                    )

                # Centered Analysis Report Heading
                st.markdown('<div style="text-align:center;"><h2 style="font-size:2.3rem; margin-bottom:2rem;">Analysis Report</h2></div>', unsafe_allow_html=True)

                # Personal Overview and Details
                st.markdown(f'''
                <div class="card" style="max-width: 1200px; margin: 0 auto;">
                    <h3 style="text-align:center;">Personal Overview</h3>
                    <div class="personal-info">
                        <h4 style="text-align:center;">{resume_data.get('name', 'Not found')}</h4>
                        <div class="details-grid">
                            <div class="details-section">
                                <p>📧 Email</p>
                                <h4>{resume_data.get('email', 'Not provided')}</h4>
                            </div>
                            <div class="details-section">
                                <p>📱 Contact</p>
                                <h4>{resume_data.get('phone', 'Not provided')}</h4>
                            </div>
                            <div class="details-section">
                                <p>📅 Experience Level</p>
                                <h4>{exp_level}</h4>
                            </div>
                            <div class="details-section">
                                <p>💼 Target Job Role</p>
                                <h4>{(get_company_role_recommendations(current_skills, top_k=1)[0]['role'] + ' at ' + get_company_role_recommendations(current_skills, top_k=1)[0]['company']) if get_company_role_recommendations(current_skills, top_k=1) else 'Not found'}</h4>
                            </div>
                            {education_html}
                            {projects_html}
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                # Technical Skills
                st.markdown('<div style="text-align:center;"><h3 style="font-size:2rem; margin-top:2.5rem;">Technical Competencies</h3></div>', unsafe_allow_html=True)
                if resume_data.get('skills'):
                    st.markdown(f'''
                    <div class="card" style="max-width: 1200px; margin: 0 auto; padding: 1.5rem 2rem;">
                        <div style="display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;">
                            {''.join([f'<span class="skill-chip">{skill}</span>' for skill in resume_data['skills']])}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.warning("No technical skills detected")

                # Recommendations
                st.markdown('<div style="text-align:center;"><h3 style="font-size:2rem; margin-top:2.5rem;">Career Development Suggestions</h3></div>', unsafe_allow_html=True)

                # Side-by-side layout for Recommended Skills and Courses
                st.markdown('<div style="height: 2.5rem;"></div>', unsafe_allow_html=True)  # Spacer
                cols = st.columns(2)
                with cols[0]:
                    st.markdown('<div style="text-align:center;"><h4 style="font-size:1.5rem; margin-top:2rem;">Recommended Skills</h4></div>', unsafe_allow_html=True)
                    rec_skills_html = '<div class="card" style="max-width: 95%; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 1.5rem; justify-content: center;">'
                    for skill in recommended_skills:
                        rec_skills_html += f'''<div style="flex: 1 1 180px; min-width: 140px; background: #f8f9fa; border-radius: 10px; padding: 1rem 1.5rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 1rem;">
                            <div style="width: 8px; height: 40px; background: #1e3d59; border-radius: 4px;"></div>
                            <span style="font-size: 1.1rem; color: #2a4b6e;">{skill}</span>
                        </div>'''
                    rec_skills_html += '</div>'
                    st.markdown(rec_skills_html, unsafe_allow_html=True)
                with cols[1]:
                    st.markdown('<div style="text-align:center;"><h4 style="font-size:1.5rem; margin-top:2rem;">Recommended Courses</h4></div>', unsafe_allow_html=True)
                    for course in recommended_courses:
                        st.markdown(f'''
                        <div class="course-card" style="width: 100%; max-width: 95%; margin: 2rem auto; display: flex; align-items: center; background: white; box-shadow: 0 4px 20px rgba(30, 61, 89, 0.1); border-radius: 12px; padding: 1.5rem;">
                            <img src="{course['thumbnail']}" 
                                 style="width: 120px; height: 80px; border-radius: 8px; object-fit: cover; margin-right: 2rem;">
                            <div style="flex: 1;">
                                <a href="{course['url']}" target="_blank" 
                                   style="font-size: 1.1rem; font-weight: 600; color: #1e3d59; text-decoration: none;">
                                    {course['title']}
                                </a>
                                <p style="margin: 12px 0; color: #4a6fa5; font-size: 1rem; line-height: 1.4;">
                                    {course['description']}
                                </p>
                                <div style="display: flex; gap: 1rem; align-items: center;">
                                    <span style="background: #e8eef4; padding: 6px 16px; border-radius: 20px; 
                                          font-size: 0.95rem; color: #1e3d59;">
                                        {course['category']}
                                    </span>
                                    <a href="{course['url']}" target="_blank" 
                                       style="color: #1e3d59; text-decoration: none; font-weight: 500;">
                                        View Course →
                                    </a>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

                # After the Recommended Courses section, add:
                st.markdown('<div style="text-align:center;"><h3 style="font-size:2rem; margin-top:2.5rem;">Recommended Company Roles</h3></div>', unsafe_allow_html=True)
                
                # Get role recommendations
                recommended_roles = get_company_role_recommendations(current_skills)
                
                # Display role recommendations with personalized to-do lists
                if recommended_roles:
                    for role in recommended_roles:
                        st.markdown(f'''
                        <div class="course-card" style="width: 100%; max-width: 95%; margin: 2rem auto; display: flex; align-items: center; background: white; box-shadow: 0 4px 20px rgba(30, 61, 89, 0.1); border-radius: 12px; padding: 1.5rem;">
                            <div style="flex: 1;">
                                <h4 style="font-size: 1.3rem; font-weight: 600; color: #1e3d59; margin-bottom: 0.5rem;">
                                    {role['role']} at {role['company']}
                                </h4>
                                <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                                    <span style="background: #e8eef4; padding: 6px 16px; border-radius: 20px; font-size: 0.95rem; color: #1e3d59;">
                                        {role['level']}
                                    </span>
                                    <span style="background: #e8eef4; padding: 6px 16px; border-radius: 20px; font-size: 0.95rem; color: #1e3d59;">
                                        {role['experience']}
                                    </span>
                                    <span style="background: #e8eef4; padding: 6px 16px; border-radius: 20px; font-size: 0.95rem; color: #1e3d59;">
                                        {role['package']}
                                    </span>
                                </div>
                                <p style="color: #4a6fa5; font-size: 1rem; line-height: 1.4;">
                                    <b>Responsibilities:</b> {role['responsibilities']}<br>
                                    <b>Language:</b> {role['language']}<br>
                                    <b>Essential Knowledge:</b> {role['knowledge']}
                                </p>
                                <details>
                                    <summary style="font-weight:600; color:#1e3d59; cursor:pointer;">Show Personalized To-Do List</summary>
                                    <div style="margin-top:1rem; color:#22223b; background:#f8f9fa; border-radius:8px; padding:1rem;">
                                        {generate_todo_list_for_role(current_skills, role)}
                                    </div>
                                </details>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.warning("No role recommendations available at the moment.")
run()