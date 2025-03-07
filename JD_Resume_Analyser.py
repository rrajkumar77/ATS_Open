import streamlit as st
import openai
import os
from dotenv import load_dotenv
import fitz
import docx

# Set page configuration at the very beginning
st.set_page_config(page_title="Resume Expert")

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(input, pdf_content, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Change to 'gpt-3.5-turbo' if needed
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"{input}\n\n{pdf_content}"}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.error(f"An error occurred while processing your request: {e}")
        return None

def input_file_setup(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text_parts = [page.get_text() for page in document]
            file_content = " ".join(text_parts)
        elif file_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            doc = docx.Document(uploaded_file)
            file_content = "\n".join([para.text for para in doc.paragraphs])
        elif file_type == "text/plain":
            file_content = uploaded_file.read().decode("utf-8")
        else:
            raise ValueError("Unsupported file type")
        return file_content
    else:
        raise FileNotFoundError("No file uploaded")

def extract_skills_from_resume(file_content):
    skills = ["Python", "Machine Learning", "Data Analysis", "Project Management"]
    return skills

## Streamlit App

st.header("JobFit Analyzer")
st.subheader('This Application helps you to evaluate the Resume Review with the Job Description')

uploaded_jd = st.file_uploader("Upload Job Description (PDF, DOC, DOCX, TXT)...", type=["pdf", "doc", "docx", "txt"])
jd_content = ""
if uploaded_jd is not None:
    jd_content = input_file_setup(uploaded_jd)
    st.write("Job Description Uploaded Successfully")
submit7 = st.button("JD Summarization")

uploaded_resume = st.file_uploader("Upload your Resume (PDF, DOC, DOCX, TXT)...", type=["pdf", "doc", "docx", "txt"])
resume_content = ""
if uploaded_resume is not None:
    resume_content = input_file_setup(uploaded_resume)
    st.write("Resume Uploaded Successfully")

submit1 = st.button("Technical Recruiter Analysis")
submit3 = st.button("Domain Expert Analysis")
submit4 = st.button("Technical Manager Analysis")
submit2 = st.button("Technical Questions")

top_skills = st.text_input("Top Skills Required for the Job (comma-separated):")
submit6 = st.button("Skill Analysis")

input_prompt = st.text_input("Queries: Feel Free to Ask here")
submit5 = st.button("Answer My Query")

input_prompt1 = """
Role: Experienced Technical Human Resource Manager with expertise in technical evaluations and Recruitment
Task: Review the provided resume against the job description.
Objective: Evaluate whether the candidate's profile aligns with the role.
Instructions:
Match Percentage: Calculate and provide the match percentage between the resume and the job description.
Professional Evaluation: Offer a detailed professional evaluation of the candidate's profile.
Strengths and Weaknesses: Highlight the strengths and weaknesses of the applicant concerning the specified job requirements.
Career Guidance: Provide career guidance based on the evaluation.
"""

input_prompt2 = """
Role: Experienced Technical Human Resource Manager with expertise in technical evaluations and Recruitment
Task: Create technical questions to evaluate the candidate based on the provided job description (JD) and resume.
Objective: Assess the candidate's technical skills and experience to the job requirements.
Instructions:
Questions from JD:
    Create a sequence of technical questions based on the job description.
    Cover all phases of a project: initiation, planning, execution, monitoring, control, and closure.
Questions from Resume:
    Create a sequence of technical questions based on the candidate's resume.
    Focus on previous project experience, technical skills, problem-solving, team collaboration, and continuous improvement.
Answers: 
    Provide answers to the questions to help the recruiter validate the candidate's responses.
"""

input_prompt3 = """
Role: Skilled ATS (Applicant Tracking System) scanner with expertise in domain and ATS functionality
Task: Evaluate the provided resume against the job description.
Objective: Assess the compatibility of the resume with the job description from a Domain Expert perspective. (Eg: Business Analyst(BA), Functional Manger or Project Manager)
Instructions:
Calculate the match percentage between the resume and job description, Provide a percentage number and explanation.
Identify any relevant keywords missing from the resume that pertain to the job description.
Your evaluation must be thorough, precise, and objective. It should ensure that the most qualified candidates are accurately identified based on their resume content in relation to the job criteria.
"""

input_prompt4 = """
Role: Skilled ATS (Applicant Tracking System) scanner with a deep understanding of the technology and Technical skills mentioned in the job description and ATS functionality
Task: Evaluate the provided resume against the job description.
Objective: Assess the compatibility of the resume with the job description from a Technical Expert perspective.
Instructions:
1. Calculate the match percentage between the resume and job description, and provide a percentage number 
2. Explain the match and the gap
3. Identify missing keywords or skills from the resume compared to the job description.
4. Create a table that includes the top 5 skills, the required years of experience (JD), the candidate's years of experience (Resume), and the relevant projects with the year they have worked on.
5. Share final thoughts on the candidate's suitability for the role.
"""

input_prompt5 = """
Role: AI Assistant
Task: Summarize the provided job description.
Objective: Provide a concise summary of the job description.
Instructions: 
Please summarize the job description and provide detailed insights about the position. 
Include key responsibilities, required qualifications, necessary skills, preferred skills, and any other important details.
"""
skills_list = []
if submit6 and top_skills:
    # Clean and validate skills input
    skills_list = [skill.strip() for skill in top_skills.split(',') if skill.strip()]
    
input_prompt6 = f"""
Role: Skill Analyst
Task: Analyze ONLY the following skills from the resume: {', '.join(skills_list)}

Instructions:
1. IMPORTANT: Analyze ONLY these specific skills: {', '.join(skills_list)}
2. For each skill listed above:
   - Check if it appears in the resume (case insensitive)
   - Identify relevant projects if mentioned
   - Years worked in that project

Output Format:
Present results in a table with exactly {len(skills_list)} rows (one for each input skill):
| Skill | Match Status | Relevant Projects | Years of Experience |
Note: 
- Include ONLY the skills listed above
- Use "NA" if project or experience information is not found
- Match Status should be "Yes" or "No" only

Additional Rules:
- Do not include any skills not listed above
- Do not add any explanatory text before or after the table
- Strictly maintain {len(skills_list)} rows in the output
"""

input_prompt7 = """
Role: AI Career Assistant  
Task: Provide a structured and precise response to the user's query based on the job description and resume.  
Objective: Extract and present relevant information **based on the type of question asked**.  
### **Instructions:**  
1. **Identify the type of query**:  
   - **Project-related** → Extract details about the mentioned project.  
   - **Job Description (JD)-related** → Summarize the job role, key responsibilities, and requirements.  
   - **Education-related** → Provide the candidate’s degrees, universities, and relevant coursework.  
   - **General Resume Inquiry** → Extract and summarize key skills, experience, or certifications.  

2. **Respond in a structured format based on the query type:**  
#### **Response Format:**  
✅ **If Project-related:**  
- **Project Name:** (If found in the resume)  
- **Work Done:** (Bullet points)  
- **Technologies Used:** (List)  
- **Key Contributions & Impact:**  

✅ **If JD-related:**  
- **Role Summary:** (One-line description)  
- **Key Responsibilities:** (Bullet points)  
- **Required Skills & Qualifications:**  

✅ **If Education-related:**  
- **Degree(s) Earned:**  
- **Institution(s):**  
- **Relevant Courses or Certifications (if mentioned):**  

✅ **If General Resume Inquiry:**  
- **Summary of Experience:**  
- **Top Skills:**  
- **Certifications (if available):**  

3. **Important Rules:**  
- If the resume **does not contain the requested information**, clearly state that instead of making assumptions.  
- If multiple relevant details exist, **prioritize the most recent and relevant ones**.  
"""


if submit1:
    if uploaded_resume is not None and uploaded_jd is not None:
        response = get_openai_response(input_prompt1, resume_content, jd_content)
        st.subheader("Technical Recruiter Analysis")
        st.write(response)
    else:
        st.write("Please upload both the Job Description and Resume to proceed.")

elif submit2:
    if uploaded_resume is not None and uploaded_jd is not None:
        response = get_openai_response(input_prompt2, resume_content, jd_content)
        st.subheader("Technical Questions")
        st.write(response)
    else:
        st.write("Please upload both the Job Description and Resume to proceed.")

elif submit3:
    if uploaded_resume is not None and uploaded_jd is not None:
        response = get_openai_response(input_prompt3, resume_content, jd_content)
        st.subheader("Domain Expert Analysis")
        st.write(response)
    else:
        st.write("Please upload both the Job Description and Resume to proceed.")

elif submit4:
    if uploaded_resume is not None and uploaded_jd is not None:
        response = get_openai_response(input_prompt4, resume_content, jd_content)
        st.subheader("Technical Manager Analysis")
        st.write(response)
    else:
        st.write("Please upload both the Job Description and Resume to proceed.")

elif submit5:
    if uploaded_resume is not None and uploaded_jd is not None:
        response = get_openai_response(input_prompt7, resume_content, jd_content)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload both the Job Description and Resume to proceed.")
        
elif submit6:
    if uploaded_resume is not None and uploaded_jd is not None:
        response = get_openai_response(input_prompt6, resume_content, jd_content)
        st.subheader("Top Skill Analysis")
        st.write(response)
    else:
        st.write("Please upload both the Job Description and Resume to proceed.")

elif submit7:
    if uploaded_jd is not None:
        response = get_openai_response(input_prompt5, "", jd_content)
        st.subheader("Job Description Summary")
        st.write(response)
    else:
        st.write("Please upload a Job Description to proceed.")
