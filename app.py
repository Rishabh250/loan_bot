import streamlit as st
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import AgentAction, AgentFinish
from typing import Union
import re
import os
import json

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class LoanDatabase:
    def __init__(self):
        self.lenders = [
            {
                "name": "HDFC Credila",
                "interest_rate": "10.0% - 12.0%",
                "maximum_amount": "INR 10,000,000",
                "about": "HDFC Credila is a trusted non-banking financial institution, offering a range of customizable loan options to meet the diverse needs of its customers.",
                "key_points": [
                    "Processing fee up to 1% + GST",
                    "Tenure up to 10 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "IDFC",
                "interest_rate": "10.15% - 12.0%",
                "maximum_amount": "INR 10,000,000",
                "about": "IDFC Bank is here to provide you with flexible loans that suit your requirements.",
                "key_points": [
                    "Processing fee up to 1% + GST",
                    "Tenure up to 12 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "ICICI",
                "interest_rate": "10.5% - 12.0%",
                "maximum_amount": "INR 20,000,000",
                "about": "ICICI is committed to offering loan solutions customized just for you.",
                "key_points": [
                    "Processing fee up to 1% + GST",
                    "Tenure up to 10 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "SBI",
                "interest_rate": "9.15% - 12.0%",
                "maximum_amount": "INR 15,000,000",
                "about": "SBI is here to serve you, with a focus on personalized loan solutions for your educational and career objectives.",
                "key_points": [
                    "Processing fee Rs 10,000 + GST",
                    "Tenure up to 15 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": False,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "Union Bank of India",
                "interest_rate": "9.8% - 12.0%",
                "maximum_amount": "INR 15,000,000",
                "about": "UBI is committed to being your guide, creating customized loan solutions for your education and career journey.",
                "key_points": [
                    "Processing fee up to Rs 5,000 + GST",
                    "Tenure up to 15 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "Avanse",
                "interest_rate": "11.5% - 12.0%",
                "maximum_amount": "INR 7,500,000",
                "about": "Avanse is known for its commitment to crafting adjustable loan options.",
                "key_points": [
                    "Processing fee up to 1%",
                    "Tenure up to 15 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "USA, Canada"
            },
            {
                "name": "Auxilo",
                "interest_rate": "11.25% - 12.0%",
                "maximum_amount": "INR 7,000,000",
                "about": "Auxilo Finserve Pvt. Ltd. is a trusted and reliable non-banking financial institution, dedicated to providing education loans to students in need.",
                "key_points": [
                    "Processing fee up to 1.5%",
                    "Tenure up to 10 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "USA, Canada, UK"
            },
            {
                "name": "Sallie Mae",
                "interest_rate": "4.15% - 15.6%",
                "maximum_amount": "100% of school-certified expenses (USD)",
                "about": "Sallie Mae is a 'US-based' powerhouse education solution company offering education financing products and resources to help students in their higher education dream big.",
                "key_points": [
                    "No origination fee",
                    "Tenure varies"
                ],
                "currency": "USD",
                "collateral_required": False,
                "non_collateral_option": True,
                "us_cosigner_required": True,
                "country": "USA",
                "university_country": "USA"
            },
            {
                "name": "Prodigy",
                "interest_rate": "13.99% - 12.0%",
                "maximum_amount": "USD 100,000",
                "about": "Prodigy is a trusted financial institution, personalized loan solutions.",
                "key_points": [
                    "Processing fee up to 5% + GST",
                    "Tenure up to 10 years"
                ],
                "currency": "USD",
                "collateral_required": False,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "USA, Canada, UK, Australia, Germany",
                "university_country": "USA, Canada, UK, Australia, Germany"
            },
            {
                "name": "Tata Capital",
                "interest_rate": "11.75% - 12.0%",
                "maximum_amount": "INR 6,500,000",
                "about": "Tata Capital is a leading financial services provider, offering competitive interest rates and maximum flexibility.",
                "key_points": [
                    "Processing fee up to 1.5% + GST",
                    "Tenure up to 10 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "Axis Bank",
                "interest_rate": "10.5%",
                "maximum_amount": "INR 20,000,000",
                "about": "Finance your studies abroad with Axis Bank's flexible loan amounts, quick disbursals and tax exemptions.",
                "key_points": [
                    "Processing fee up to 1% + GST",
                    "Tenure up to 10 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "Incred",
                "interest_rate": "11.25%",
                "maximum_amount": "INR 10,000,000",
                "about": "Invest in your education without worries, with Incred's wide range of loans covering 100% of your tuition fees*.",
                "key_points": [
                    "Processing fee up to 1.5% + GST",
                    "Tenure up to 12 years"
                ],
                "currency": "INR",
                "collateral_required": True,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "India",
                "university_country": "Any"
            },
            {
                "name": "Ascent",
                "interest_rate": "3.79% - 9.9%",
                "maximum_amount": "USD 400,000",
                "about": "Ascent is a trusted financial institution, committed to providing customizable loan solutions.",
                "key_points": [
                    "0% processing fee",
                    "Tenure up to 10 years"
                ],
                "currency": "USD",
                "collateral_required": False,
                "non_collateral_option": True,
                "us_cosigner_required": True,
                "country": "USA",
                "university_country": "USA"
            },
            {
                "name": "Earnest",
                "interest_rate": "4.25% - 9.0%",
                "maximum_amount": "USD 250,000",
                "about": "Earnest is a renowned US non-banking financial institution that provides flexible and personalized loans.",
                "key_points": [
                    "0% processing fee",
                    "Tenure up to 10 years"
                ],
                "currency": "USD",
                "collateral_required": False,
                "non_collateral_option": True,
                "us_cosigner_required": False,
                "country": "USA",
                "university_country": "USA"
            }
        ]

    def get_loan_options(self, details):
        return json.dumps(self.lenders)

loan_db = LoanDatabase()

tools = [
    Tool(
        name="Loan Database",
        func=loan_db.get_loan_options,
        description="Retrieves all available loan options."
    )
]

def format_lenders_data(lenders):
    formatted_data = []
    for lender in lenders:
        lender_info = f"""
        {lender['name']}: 
        - Interest Rate: {lender['interest_rate']}
        - Maximum Amount: {lender['maximum_amount']}
        - About: {lender['about']}
        - Key Points: {', '.join(lender['key_points'])}
        - Currency: {lender['currency']}
        - Collateral Required: {lender['collateral_required']}
        - Non-Collateral Option: {lender['non_collateral_option']}
        - US Cosigner Required: {lender['us_cosigner_required']}
        - Country: {lender['country']}
        - University Country: {lender['university_country']}
        """
        formatted_data.append(lender_info.strip())
    
    return "\n".join(formatted_data)

class CounselorPromptTemplate(StringPromptTemplate):
    template = """You are Sarah, a friendly education loan counselor with 15 years of experience. Your goal is to help students find the best loan options. Respond like a real person in a casual conversation.

IMPORTANT: 
1. Gather this info naturally:
   - Full name
   - Age
   - Nationality
   - Current residence
   - Desired course and university
   - Estimated education cost
   - US cosigner availability
   - Collateral availability
   - Academic credentials
   - Work experience

2. Only suggest loans after gathering all info.

3. Use ONLY the Loan Database info. Don't make up details.

4. Loan Database fields:
   - name
   - interest_rate
   - maximum_amount
   - about
   - key_points
   - currency
   - collateral_required
   - non_collateral_option
   - us_cosigner_required
   - country
   - university_country

Lenders information:
{lenders_data}

Your response should:
- Be brief and to the point
- Sound natural and friendly
- Ask for info casually
- Give advice based only on the Loan Database
- Use exact lender details from the database

Student details: {student_details}
Conversation so far:
{conversation_history}

Student's last message: {student_message}

Your response (as Sarah):"""

    def format(self, **kwargs) -> str:
        kwargs["tool_names"] = ", ".join([tool.name for tool in tools])
        lenders_data = format_lenders_data(loan_db.lenders)
        return self.template.format(lenders_data=lenders_data, **kwargs)
class CounselorOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Response:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Response:")[-1].strip()},
                log=llm_output,
            )

        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            return AgentFinish(
                return_values={"output": llm_output.strip()},
                log=llm_output,
            )
        action = match.group(1).strip()
        action_input = match.group(2).strip()
        return AgentAction(tool=action, tool_input=action_input, log=llm_output)

class EducationLoanCounselorBot:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
        self.prompt = CounselorPromptTemplate(input_variables=["student_details", "conversation_history", "student_message"])
        self.output_parser = CounselorOutputParser()
        self.counselor_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.agent = LLMSingleActionAgent(
            llm_chain=self.counselor_chain,
            output_parser=self.output_parser,
            stop=["\nStudent:"],
            allowed_tools=[tool.name for tool in tools]
        )
        self.executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=True)
        self.conversation_history = ""
        self.student_details = ""

    def get_response(self, user_input):
        if not self.student_details:
            self.student_details = user_input
        response = self.executor.run(
            student_details=self.student_details,
            conversation_history=self.conversation_history,
            student_message=user_input
        )
        self.conversation_history += f"Student: {user_input}\nSarah: {response}\n"
        return response

def main():
    st.set_page_config(page_title="Education Loan Counselor", page_icon="💼", layout="wide")
    st.title("Education Loan Counselor ChatBot")

    # Initialize session state
    if "bot" not in st.session_state:
        st.session_state.bot = EducationLoanCounselorBot()
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.bot.get_response(prompt)
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Sidebar with instructions
    st.sidebar.title("Instructions")
    st.sidebar.write("""
    1. Start by providing your details (name, age, nationality, degree, university, GPA, and study plans).
    2. Ask questions about education loans or seek advice.
    3. The AI counselor, Sarah, will assist you in finding the best loan options.
    4. Continue the conversation until you have all the information you need.
    """)

if __name__ == "__main__":
    main()
