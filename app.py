"""
This is the main application file for the loan counselor agent.

This application provides a Flask-based REST API for a loan counseling chatbot
that helps students understand their loan options. It handles user conversations,
validates requests, and provides loan recommendations through an AI-powered
counselor agent.

Key Features:
- Chat endpoint for conversing with the loan counselor
- Request validation for required student information
- Conversation memory management
- Error handling and logging
- CORS support for cross-origin requests
- Asynchronous processing using thread pools
"""
import os
from http import HTTPStatus
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple
try:
    from dotenv import load_dotenv
    from flask import Flask, request, jsonify, Response
    from langsmith import traceable
    from flask_cors import CORS
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install required packages: pip install python-dotenv flask langsmith flask-cors")
    raise

from loan_counselor_agent import LoanCounselorAgent

# Load environment variables and configure app
def create_app() -> Flask:
    """
    Create and configure Flask application with necessary settings.
    
    Returns:
        Flask: Configured Flask application instance
    """
    load_dotenv()

    flask_app = Flask(__name__)
    CORS(flask_app)

    # Get config values from environment with defaults
    flask_app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'loan-counselor-agent'),
        DEBUG=os.getenv('FLASK_DEBUG', 'true').lower() == 'true',
        ENV=os.getenv('FLASK_ENV', 'development'),
        HOST=os.getenv('FLASK_HOST', '0.0.0.0'),
        PORT=int(os.getenv('FLASK_PORT', '8000'))
    )

    return flask_app

# Initialize Flask app and counselor
app = create_app()
counselor = LoanCounselorAgent()

# Configure LangChain environment
def configure_langchain() -> None:
    """
    Configure LangChain environment variables for AI model integration.
    Sets up API keys and tracing settings.
    """
    os.environ.update({
        "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY", ""),
        "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY", ""),
        "LANGCHAIN_TRACING_V2": "true",
        "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT", "loan-counselor-agent")
    })

configure_langchain()

# Required fields for request validation
REQUIRED_REQUEST_FIELDS = ['message', 'student_details', 'userId']
REQUIRED_STUDENT_FIELDS = [
    'name',
    'origin_country',
    'destination_country', 
    'loan_amount_needed',
    'course_of_study'
]

def validate_request_data(data: Dict[str, Any]) -> Tuple[Dict[str, str], int]:
    """
    Validate the incoming request data for required fields and student information.
    
    Args:
        data (Dict[str, Any]): Request data containing message and student details
        
    Returns:
        Tuple[Dict[str, str], int]: Error response and HTTP status code if validation fails,
                                   empty dict and OK status if validation passes
    """
    if not data:
        return {'error': 'Request body is empty'}, HTTPStatus.BAD_REQUEST

    # Validate required fields
    missing_fields = [field for field in REQUIRED_REQUEST_FIELDS if field not in data]
    if missing_fields:
        return {
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }, HTTPStatus.BAD_REQUEST

    # Validate student details
    student_details = data.get('student_details', {})
    if not isinstance(student_details, dict):
        return {'error': 'student_details must be a JSON object'}, HTTPStatus.BAD_REQUEST
        
    missing_student_fields = [
        field for field in REQUIRED_STUDENT_FIELDS
        if field not in student_details
    ]
    if missing_student_fields:
        return {
            'error': f'Missing required student details: {", ".join(missing_student_fields)}'
        }, HTTPStatus.BAD_REQUEST

    return {}, HTTPStatus.OK

# Initialize thread pool for handling concurrent requests
executor = ThreadPoolExecutor(max_workers=3)

def get_cached_response(message: str, user_id: str, student_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve cached response from the counselor if available.
    
    Args:
        message (str): User's message
        user_id (str): Unique identifier for the user
        student_details (Dict): Student information
        
    Returns:
        Dict[str, Any]: Cached response if available, None otherwise
    """
    try:
        return counselor.get_loan_recommendation(
            student_message=message,
            user_id=user_id,
            student_details=student_details
        )
    except Exception:
        return None

def handle_chat_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Process chat requests and generate appropriate responses.
    
    Args:
        data (Dict[str, Any]): Request data containing message and student details
        
    Returns:
        Tuple[Dict[str, Any], int]: Response data and HTTP status code
    """
    error_response, status_code = validate_request_data(data)
    if error_response:
        return error_response, status_code

    message = data['message']
    user_id = data['userId']
    student_details = data['student_details']
    student_details['userId'] = user_id

    if message.lower() == 'reset':
        counselor.reset_conversation(user_id)
        return {'response': 'Conversation reset successfully'}, HTTPStatus.OK

    # Use cached response if available
    response = get_cached_response(message, user_id, student_details)
    if not response:
        try:
            future = executor.submit(
                # counselor.get_loan_recommendation,
                student_details,
                message,
                user_id
            )
            response = future.result(timeout=30)
        except TimeoutError:
            return {'error': 'Request timed out'}, HTTPStatus.REQUEST_TIMEOUT
        except Exception as e:
            return {'error': f'Error getting recommendation: {str(e)}'}, HTTPStatus.INTERNAL_SERVER_ERROR
            
    return {'response': response}, HTTPStatus.OK

@traceable(project_name="loan-counselor-agent")
@app.route('/chat', methods=['POST'])
def chat() -> Response:
    """
    API endpoint for chatting with the loan counselor.
    Handles incoming chat requests and returns counselor responses.
    
    Returns:
        Response: JSON response containing counselor's message or error
    """
    try:
        response, status_code = handle_chat_request(request.json)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/reset', methods=['POST']) 
def reset_memory() -> Response:
    """
    API endpoint for clearing conversation memory for users.
    Allows users to start fresh conversations with the counselor.
    
    Returns:
        Response: JSON response indicating success or error
    """
    try:
        data = request.json
        if not data or 'userId' not in data:
            return jsonify({'error': 'Missing userId in request'}), HTTPStatus.BAD_REQUEST

        counselor.reset_conversation(data['userId'])
        return jsonify({'message': 'Conversation history cleared successfully'})
    except Exception as e:
        return jsonify({
            'error': f'Error clearing conversation histories: {str(e)}'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/user-report', methods=['POST'])
def user_report() -> Response:
    """
    API endpoint for getting user conversation reports.
    
    Returns:
        Response: JSON response containing user report or error
    """
    try:
        if not request.json or 'userId' not in request.json:
            return jsonify({'error': 'Missing userId in request'}), HTTPStatus.BAD_REQUEST
            
        response = counselor.get_user_report(request.json['userId'])
        return jsonify(response), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': f'Error getting user report: {str(e)}'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.errorhandler(404)
def not_found() -> Tuple[Response, int]:
    """
    Handle 404 Not Found errors.
    Returns a JSON response for invalid routes.
    """
    return jsonify({'error': 'Not found'}), HTTPStatus.NOT_FOUND

@app.errorhandler(500)
def internal_error() -> Tuple[Response, int]:
    """
    Handle 500 Internal Server errors.
    Returns a JSON response for server-side errors.
    """
    return jsonify({'error': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    # Run Flask app
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )