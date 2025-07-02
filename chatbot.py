import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF
import docx
import easyocr
import re

# Initialize OpenAI client
client = OpenAI(api_key="YOUR_API_KEY_HERE")  # Replace with your actual OpenAI API key


# --- PROMPT ---
prompt = """<Role>
You are an expert Interview Analysis System combining the expertise of an intern, trainee, junior, and senior hiring manager, behavioral psychologist, body language expert, and negotiation strategist. Your goal is to help candidates master job interviews through deep analysis and strategic preparation.
</Role>

<Context>
The job interview process is complex, involving verbal and non-verbal communication, psychological dynamics, and strategic negotiation. Success requires understanding both explicit and implicit expectations from the employer's perspective.
</Context>

<Instructions>
1. Analyze the provided CV and job description to identify key competencies, company culture, and role-specific expectations.
2. Generate exactly 10 interview questions (2 HR-based, 8 technical) tailored to the CV and job description.
3. For each question, provide:
   - A sample answer based on the CV and job description.
   - Key points the answer should cover to be considered accurate.
4. When evaluating user responses:
   - Assess relevance, completeness, and alignment with job requirements.
   - Assign an accuracy score (0-100%) based on how well the response addresses the question and incorporates key points.
   - Provide constructive feedback highlighting strengths and areas for improvement.
</Instructions>

<Constraints>
- Stay focused on practical, actionable advice.
- Base recommendations on proven psychological principles.
- Maintain professional boundaries and ethical guidelines.
- Personalize advice based on the specific role and CV.
</Constraints>

<Output_Format>
Q1: <question>
A1: <sample answer>
Key Points: <key points>
...
Q10: <question>
A10: <sample answer>
Key Points: <key points>
</Output_Format>"""

# --- FILE PARSING ---
def extract_text(file):
    try:
        if file.type == "application/pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        elif file.type.startswith("text"):
            return str(file.read(), "utf-8")
        elif file.type.endswith(("png", "jpg", "jpeg")):
            reader = easyocr.Reader(['en'])
            result = reader.readtext(file.read())
            return " ".join([detection[1] for detection in result])
        else:
            return "Unsupported file type."
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return ""

# --- QUESTION GENERATION ---
def generate_questions(cv_text, jd_text):
    full_prompt = prompt + "\n\nCV:\n" + cv_text + "\n\nJob Description:\n" + jd_text
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Act as a professional HR and technical interviewer."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return ""

# --- PARSE QUESTIONS ---
def parse_questions(questions_text):
    questions = []
    try:
        blocks = re.split(r'Q\d+:', questions_text)[1:]
        for i, block in enumerate(blocks):
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                question = lines[0].strip()
                sample_answer = lines[1].replace("A" + str(i+1) + ":", "").strip()
                key_points = lines[2].replace("Key Points:", "").strip()
                questions.append({
                    "question": question,
                    "sample_answer": sample_answer,
                    "key_points": key_points
                })
        return questions
    except Exception as e:
        st.error(f"Error parsing questions: {str(e)}")
        return []

# --- UI SETUP ---
st.set_page_config(page_title="Smart CV & JD Interview Bot", layout="wide")
st.title("🤖 Smart Interview Bot")
st.markdown("Upload your CV, provide a job description, and engage in a live interview with final feedback.")

col1, col2 = st.columns(2)
with col1:
    cv_file = st.file_uploader("Upload CV", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
with col2:
    jd_text = st.text_area("Enter Job Description", height=150)

if 'state' not in st.session_state:
    st.session_state.state = {
        'questions': [],
        'current_question_index': 0,
        'user_responses': [],
        'feedback': [],
        'chat_started': False
    }

if st.button("Start Interview", key="start_button_unique"):
    if not cv_file or not jd_text:
        st.error("Please upload a CV and provide a job description.")
    else:
        with st.spinner("Processing files and generating questions..."):
            cv_text = extract_text(cv_file)
            if cv_text and cv_text != "Unsupported file type.":
                questions_text = generate_questions(cv_text, jd_text)
                questions = parse_questions(questions_text)
                if questions:
                    st.session_state.state = {
                        'questions': questions,
                        'current_question_index': 0,
                        'user_responses': [],
                        'feedback': [],
                        'chat_started': True
                    }
                    st.rerun()
                else:
                    st.error("Failed to parse or generate questions.")
            else:
                st.error("Failed to process CV.")

# --- INTERVIEW SESSION ---
if st.session_state.state['chat_started'] and st.session_state.state['current_question_index'] < len(st.session_state.state['questions']):
    q_idx = st.session_state.state['current_question_index']
    question = st.session_state.state['questions'][q_idx]['question']

    st.markdown(f"### Q{q_idx + 1}: {question}")

    with st.form(key=f"form_{q_idx}"):
        user_input = st.text_area("Your Answer", key=f"input_{q_idx}")
        submit = st.form_submit_button("Submit")

        if submit:
            if user_input.strip():
                st.session_state.state['user_responses'].append(user_input.strip())
                st.session_state.state['current_question_index'] += 1
                st.rerun()
            else:
                st.error("Answer cannot be empty.")

# --- FINAL EVALUATION ---
elif st.session_state.state['chat_started'] and st.session_state.state['current_question_index'] >= len(st.session_state.state['questions']) and not st.session_state.state['feedback']:
    st.markdown("### ✅ Interview Complete")
    st.markdown("Here are your responses:")

    for i, (q, a) in enumerate(zip(st.session_state.state['questions'], st.session_state.state['user_responses'])):
        st.markdown(f"**Q{i+1}:** {q['question']}")
        st.markdown(f"**Your Answer:** {a}")
        st.markdown("---")

    eval_prompt = """Evaluate the following interview answers collectively.

- Provide ONE combined feedback paragraph that summarizes the candidate's overall performance, strengths, and areas to improve.
- Then assign ONE overall accuracy score (0–100%).
- Format the output exactly as:
Feedback: <your paragraph>
Score: <numeric score>%\n\n
Only follow that format.

Interview Questions and Answers:\n\n"""
    for i, (q, a) in enumerate(zip(st.session_state.state['questions'], st.session_state.state['user_responses'])):
        eval_prompt += f"Q{i+1}: {q['question']}\nA{i+1}: {a}\n\n"

    with st.spinner("Evaluating your answers..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Act as an expert interviewer evaluating answers collectively."},
                    {"role": "user", "content": eval_prompt}
                ],
                temperature=0.7,
            )
            result = response.choices[0].message.content.strip()
            feedback_match = re.search(r"Feedback:\s*(.*?)\nScore:", result, re.DOTALL)
            score_match = re.search(r"Score:\s*(\d+)", result)

            feedback = feedback_match.group(1).strip() if feedback_match else "No feedback provided."
            score = int(score_match.group(1)) if score_match else 0

            st.session_state.state['feedback'] = [feedback, score]

            st.markdown("### 📋 Overall Feedback")
            st.markdown(feedback)
            st.markdown(f"### 🎯 Final Score: **{round(score / 10, 1)} / 10**")

        except Exception as e:
            st.error(f"Evaluation failed: {str(e)}")
