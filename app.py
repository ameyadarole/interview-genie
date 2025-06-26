import streamlit as st
import hmac
import pdfplumber
import google.generativeai as genai

# --- Initialize logout state ---
if "logout_triggered" not in st.session_state:
    st.session_state["logout_triggered"] = False

# --- Page Config ---
st.set_page_config(page_title="Interview Genie Login", page_icon="🧞", layout="centered")

# --- Authenticate Gemini ---
genai.configure(api_key=st.secrets["google"]["api_key"])
gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")

# --- Password Protection ---

# def check_password():

#     def login_form():
#         st.image("genie.jpg", width=200)
#         st.markdown("### 🔐 Welcome to Interview Genie")
#         st.markdown("Enter your credentials to unlock personalized interview prep magic!")

#         with st.form("Credentials"):
#             st.text_input("👤 Username", key="username")
#             st.text_input("🔑 Password", type="password", key="password")
#             st.form_submit_button("✨ Log in", on_click=password_entered)

#     def password_entered():
#         if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
#             st.session_state["password"],
#             st.secrets.passwords[st.session_state["username"]],
#         ):
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]
#             del st.session_state["username"]
#         else:
#             st.session_state["password_correct"] = False

#     if st.session_state.get("password_correct", False):
#         return True

#     login_form()
#     if "password_correct" in st.session_state:
#         st.error("😕 User not known or password incorrect")
#     return False

def check_password():
    def login_form():
        st.image("genie.jpg", width=200)
        st.markdown("### 🔐 Welcome to Interview Genie")
        st.markdown("Enter your credentials to unlock personalized interview prep magic!")

        with st.form("Credentials"):
            st.text_input("👤 Username", key="username")
            st.text_input("🔑 Password", type="password", key="password")
            st.form_submit_button("✨ Log in", on_click=password_entered)

    def password_entered():
        if st.session_state.get("username") in st.secrets["passwords"] and hmac.compare_digest(
            st.session_state.get("password", ""),
            st.secrets["passwords"][st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # ✅ Show logout message once after session reset
    if st.session_state.get("logout_success"):
        st.success("✅ Logout successful!")
        del st.session_state["logout_success"]

    if st.session_state.get("password_correct", False):
        return True

    login_form()

    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 User not known or password incorrect")

    return False

if not check_password():
    st.stop()

# --- Welcome ---
st.success("✅ Login successful! The genie is ready to help you crack your interviews.")

# --- Input Section ---
st.markdown("## 📄 Paste or Upload Your Resume & Job Description")

job_description = st.text_area("📝 Paste the Job Description here", height=250)

st.markdown("### 📌 Provide Your Resume")
upload_option = st.radio("Choose input method for your resume:", ("📎 Upload PDF", "✍️ Paste Text"))

resume_text = ""

# if upload_option == "📎 Upload PDF":
#     uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])
#     if uploaded_file is None:
#         st.warning("📂 Please upload a PDF resume to proceed.")
#     else:
#         with pdfplumber.open(stream=uploaded_file.read(), filetype="pdf") as doc:
#             resume_text = "\n".join(page.get_text() for page in doc)
#         st.success("📄 Resume text extracted from PDF.")
#         st.text_area("🧾 Extracted Resume Text", resume_text, height=250)
# else:
#     resume_text = st.text_area("✍️ Paste your Resume content here", height=250)

if upload_option == "📎 Upload PDF":
    uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])
    if uploaded_file is None:
        st.warning("📂 Please upload a PDF resume to proceed.")
    else:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                resume_text = "\n".join(
                    page.extract_text() for page in pdf.pages if page.extract_text()
                )
            st.success("📄 Resume text extracted from PDF.")
            st.text_area("🧾 Extracted Resume Text", resume_text, height=250)
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")
else:
    resume_text = st.text_area("✍️ Paste your Resume content here", height=250)

if job_description.strip() and resume_text.strip():
    st.success("✅ Both Job Description and Resume received.")

    if st.button("🔍 Run Skill Gap Assessment with Gemini"):
        with st.spinner("💫 Letting the Genie analyze with Gemini Flash..."):

            prompt = f"""
            You are an expert career coach.
            
            Analyze the following job description (JD) and resume. 

            Give a brief idea about the desired role or profile from job description in 2-3 lines.
            
            Extract the **most relevant skills from JD** (technical and soft skills) from job description and display.

            Then compare them, and return the results in this format:
            
            ### ✅ Skills You Already Have
            - skill 1
            - skill 2

            ### 📚 Skills You Need to Gain
            - skill 3
            - skill 4

            Then calculate and show a final:
            ### 🧮 Skill Match Score
            Return a score (0–100%) showing how closely the user's skills match the JD based on overlap.

             ### 📚 Suggested Courses/Resources
            For each skill in the 'Skills You Need to Gain' list, suggest a top 3 online courses/resources from YouTube / Coursera / Udemy / LinkedIn Learning in bullet points.
            With a bullet point, give a clickable link of the course/resources.
             ### 📚 Further Roadmap(80-20 Rule)
            You need to give a roadmap based on 80-20 rule. Give a list of crucial concepts you need to master in bullet points.

            If the resume and job description are identical, the skill gap should be empty.

            Be precise. Avoid vague or generic words.

            -----

            **Job Description:**
            {job_description}

            **Resume:**
            {resume_text}
            """

            response = gemini_model.generate_content(prompt)
            output = response.text

        import re
        from fpdf import FPDF
        import base64

        # --- Clean text ---
        def strip_unicode(text):
            # Remove emojis and non-latin-1 characters
            return re.sub(r"[^\x00-\xFF]", "", text)

        # --- Enhanced PDF class ---

        
        class PDF(FPDF):
            def __init__(self):
                 super().__init__()
                 self.first_page = True  # Track if it's the first page

            def header(self):
                if self.first_page:
                    self.image("genie.jpg", 10, 8, 20)  # Adjust as needed
                    self.set_font("Arial", 'B', 14)
                    self.cell(0, 10, "Interview Genie Assessment Report", ln=True, align="C")
                    self.ln(10)
                    self.first_page = False  # Disable header from next page onward
                    
            def add_text(self, text):
                self.set_font("Arial", size=12)
                lines = text.split("\n")
                for line in lines:
                    md_links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', line)
                    if md_links:
                        for label, url in md_links:
                            self.set_text_color(0, 0, 255)
                            self.set_font("Arial", 'U', 12)
                            self.cell(0, 10, label, ln=True, link=url)
                            self.set_text_color(0, 0, 0)
                            self.set_font("Arial", size=12)
                    else:
                        self.multi_cell(0, 10, line)

        # --- Generate PDF ---
        def generate_pdf(text):
            pdf = PDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            clean_text = strip_unicode(text)
            pdf.add_text(clean_text)
            pdf_file_path = "Skill_Gap_Report.pdf"
            pdf.output(pdf_file_path)
            return pdf_file_path

        # --- Show in Streamlit ---
        st.markdown("## 🧠 Skill Gap Assessment by Gemini")
        st.markdown(output if output else "❌ Gemini did not return a valid response.")

        # --- Only if output exists ---
        if output:
            clean_output = strip_unicode(output)
            pdf_path = generate_pdf(clean_output)

            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                href = f'<a href="data:application/pdf;base64,{base64_pdf}" download="Skill_Gap_Report.pdf">📥 Download Skill Gap Report (PDF)</a>'
                st.markdown(href, unsafe_allow_html=True)



# 🧠 Follow-up chat with Gemini
st.markdown("##### 💬 Ask Gemini anything about this job or your resume:")

# 💡 Subtle examples as guidance
st.markdown(
    "<span style='font-size: 0.85em; color: gray;'>e.g. “What should I learn first?”, “Give me a 7-day learning plan”, “Create a LinkedIn headline for me”</span>",
    unsafe_allow_html=True
)

user_query = st.text_area("", height=100, max_chars=500)

if user_query:
    with st.spinner("🤖 Gemini is thinking..."):
        followup = gemini_model.generate_content(
            f"""
            Based on the same Job Description and Resume:
            
            **Job Description:**
            {job_description}
            
            **Resume:**
            {resume_text}
            
            Now answer this user query:
            {user_query}
            """
        )
        with st.chat_message("ai"):
            st.markdown(followup.text)


else:
    st.info("📥 Please provide both Job Description and Resume to continue.")

st.markdown("---")
st.markdown("### 🔒 End of Session")

if st.button("🚪 Logout"):
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["logout_success"] = True
    st.rerun()

