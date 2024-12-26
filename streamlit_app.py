import streamlit as st
import requests

# Configure page layout and style
st.set_page_config(
    page_title="Student Loan Counselor",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    .response-box {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        background-color: #f4f4f4;
        font-size: 16px;
        color: #333;
        overflow-y: auto;
        height: 200px;
    }
    </style>
""", unsafe_allow_html=True)

# Header section with title and description
st.title("🎓 Student Loan Counselor AI")
st.markdown("""
    Your AI-powered assistant for navigating international student loans.
    Get personalized guidance and recommendations for your education financing journey.
""")

# Layout with two sections
col1, col2 = st.columns([1, 2])

# User Information
with col1:
    st.markdown("## 👤 User Information")
    user_id = st.text_input("User ID", placeholder="Enter your unique ID")

    st.markdown("## 📝 Student Details")
    student_details = {
        "name": st.text_input("Full Name", placeholder="Enter your full name"),
        "origin_country": st.text_input("Origin Country", placeholder="Your home country"),
        "destination_country": st.text_input("Destination Country", placeholder="Where you plan to study"),
        "loan_amount_needed": st.number_input("Loan Amount Needed ($)", min_value=0, format="%d"),
        "course_of_study": st.text_input("Course of Study", placeholder="Your intended program")
    }

# Chat Interface
with col2:
    st.markdown("## 💬 Chat Interface")
    message = st.text_area("Your Message", placeholder="Type your message here...", height=150)

    if st.button("📤 Send Message"):
        if user_id and message:
            with st.spinner('Processing your message...'):
                try:
                    response = requests.post(
                        "http://localhost:8000/chat",
                        json={
                            "userId": user_id,
                            "message": message,
                            "student_details": student_details
                        }
                    )
                    response.raise_for_status()

                    data = response.json()
                    if 'response' in data:
                        st.markdown("### 🤖 AI Response:")
                        # Create the big box for the response
                        st.markdown(
                            f"<div class='response-box'>{data['response']['response']}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.error(data.get('error', 'An unknown error occurred'))
                except requests.RequestException as e:
                    st.error(f"🚫 Connection error: {str(e)}")
        else:
            st.warning("⚠️ Please provide both User ID and Message.")

    # Buttons for resetting chat and generating report
    col_reset, col_report = st.columns([1, 1])

    with col_reset:
        if st.button("🔄 Reset Chat"):
            if user_id:
                with st.spinner('Resetting conversation...'):
                    try:
                        response = requests.post(
                            "http://localhost:8000/reset",
                            json={"userId": user_id}
                        )
                        response.raise_for_status()
                        data = response.json()
                        if 'message' in data:
                            st.success("✅ " + data['message'])
                        else:
                            st.error(data.get('error', 'An unknown error occurred'))
                    except requests.RequestException as e:
                        st.error(f"🚫 Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please provide User ID to reset conversation.")

    with col_report:
        if st.button("📊 Generate Report"):
            if user_id:
                with st.spinner('Generating report...'):
                    try:
                        response = requests.post(
                            "http://localhost:8000/user-report",
                            json={"userId": user_id}
                        )
                        response.raise_for_status()
                        report_data = response.json()

                        if 'error' not in report_data:
                            st.markdown("### 📈 Conversation Analysis")
                            st.metric("Total Messages", report_data['conversation_length'])
                            sentiment = report_data['sentiment_analysis']
                            st.write(sentiment)
                            st.markdown("#### 📝 Summary")
                            st.info(report_data['user_summary'])
                        else:
                            st.error(report_data['error'])
                    except requests.RequestException as e:
                        st.error(f"🚫 Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please provide User ID to generate report.")
