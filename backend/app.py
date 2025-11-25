"""Flask Backend API for PythonBuddy
Created originally by Ethan Chiu 10/25/16
v3.0.0 - Refactored with separate backend/frontend architecture

Backend API providing Python code linting and execution
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
from datetime import datetime
from pylint import epylint as lint
from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Pool, cpu_count
from pylint_errors.pylint_errors import pylint_dict_final


def is_os_linux():
    """Check if OS is Linux-based"""
    if os.name == "nt":
        return False
    return True


# Configure Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)  # Enable CORS for React frontend

# Get number of cores for multiprocessing
num_cores = cpu_count()

# Store session data (in production, use Redis or similar)
sessions = {}


def get_session_id():
    """Get or create session ID from request"""
    return request.headers.get('X-Session-ID', 'default')

@app.route('/', methods=['GET'])
def root():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/api/check_code', methods=['POST'])
def check_code():
    """Run pylint on code and get output

    Request JSON:
        {
            "code": "python code string"
        }

    Returns:
        JSON array of pylint errors:
        [
            {
                "code": "E0602",
                "error": "undefined-variable",
                "message": "Undefined variable 'x'",
                "line": "5",
                "error_info": "..."
            },
            ...
        ]
    """
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "No code provided"}), 400

    code = data['code']
    session_id = get_session_id()

    # Initialize session if needed
    if session_id not in sessions:
        sessions[session_id] = {
            "count": 0,
            "time_now": datetime.now(),
            "file_name": None
        }

    output = evaluate_pylint(code, session_id)
    return jsonify(output)


@app.route('/api/run_code', methods=['POST'])
def run_code():
    """Run python 3 code

    Request JSON:
        {
            "code": "python code string"
        }

    Returns:
        JSON with output:
        {
            "output": "program output"
        }
    """
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "No code provided"}), 400

    code = data['code']
    session_id = get_session_id()

    # Initialize session if needed
    if session_id not in sessions:
        sessions[session_id] = {
            "count": 0,
            "time_now": datetime.now(),
            "file_name": None
        }

    # Rate limiting
    if slow(session_id):
        return jsonify({
            "error": "Running code too much within a short time period. Please wait a few seconds before clicking 'Run' each time."
        }), 429

    sessions[session_id]["time_now"] = datetime.now()

    # Write code to temp file
    if not sessions[session_id]["file_name"]:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp:
            sessions[session_id]["file_name"] = temp.name
            temp.write(code.encode('utf-8'))
    else:
        with open(sessions[session_id]["file_name"], 'w') as f:
            f.write(code)

    # Execute code
    cmd = f'python {sessions[session_id]["file_name"]}'
    try:
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
                  stderr=STDOUT, close_fds=True)
        output, _ = p.communicate(timeout=5)  # 5 second timeout
        return jsonify({"output": output.decode('utf-8')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def slow(session_id):
    """Rate limiting check"""
    sessions[session_id]["count"] += 1
    time = datetime.now() - sessions[session_id]["time_now"]
    if time.total_seconds() == 0:
        return False
    if float(sessions[session_id]["count"]) / float(time.total_seconds()) > 5:
        return True
    return False


def evaluate_pylint(text, session_id):
    """Create temp files for pylint parsing on user code

    Args:
        text: user code
        session_id: session identifier

    Returns:
        list of dictionaries containing pylint errors
    """
    # Create or update temp file
    if sessions[session_id]["file_name"]:
        with open(sessions[session_id]["file_name"], "w") as f:
            f.write(text)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp:
            sessions[session_id]["file_name"] = temp.name
            temp.write(text.encode("utf-8"))

    try:
        ARGS = " -r n --disable=R,C"
        (pylint_stdout, pylint_stderr) = lint.py_run(
            sessions[session_id]["file_name"] + ARGS, return_std=True)
    except Exception as e:
        return {"error": str(e)}

    if pylint_stderr.getvalue():
        return {"error": "Issue with pylint configuration"}

    return format_errors(pylint_stdout.getvalue())


def process_error(error):
    """Formats error message into dictionary

    Args:
        error: pylint error full text

    Returns:
        dictionary of error or None
    """
    # Return None if not an error or warning
    if error == " " or error is None:
        return None
    if error.find("Your code has been rated at") > -1:
        return None

    list_words = error.split()
    if len(list_words) < 3:
        return None

    # Detect OS and extract line number
    line_num = None
    try:
        if is_os_linux():
            line_num = error.split(":")[1]
        else:
            line_num = error.split(":")[2]
    except Exception:
        return None

    # Parse error details
    error_yet, message_yet, first_time = False, False, True
    i, length = 0, len(list_words)
    error_code = None
    error_string = None
    full_message = None

    while i < length:
        word = list_words[i]
        if (word == "error" or word == "warning") and first_time:
            error_yet = True
            first_time = False
            i += 1
            continue
        if error_yet:
            error_code = word[1:-1]
            error_string = list_words[i + 1][:-1]
            i = i + 3
            error_yet = False
            message_yet = True
            continue
        if message_yet:
            full_message = ' '.join(list_words[i:length - 1])
            break
        i += 1

    if not error_code or error_code not in pylint_dict_final:
        return None

    error_info = pylint_dict_final[error_code]

    return {
        "code": error_code,
        "error": error_string,
        "message": full_message,
        "line": line_num,
        "error_info": error_info,
    }


def format_errors(pylint_text):
    """Format errors into parsable list

    Args:
        pylint_text: original pylint output

    Returns:
        list of error dictionaries
    """
    errors_list = pylint_text.splitlines(True)

    # If there is not an error, return empty list
    if len(errors_list) > 2 and \
            "--------------------------------------------------------------------" in errors_list[1] and \
            "Your code has been rated at" in errors_list[2] and "module" not in errors_list[0]:
        return []

    if len(errors_list) > 0:
        errors_list.pop(0)

    pylint_dict = []
    try:
        pool = Pool(num_cores)
        pylint_dict = pool.map(process_error, errors_list)
        # Filter out None values
        pylint_dict = [e for e in pylint_dict if e is not None]
    finally:
        pool.close()
        pool.join()

    return pylint_dict


@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """Cleanup session temp files"""
    session_id = get_session_id()
    if session_id in sessions and sessions[session_id]["file_name"]:
        try:
            os.remove(sessions[session_id]["file_name"])
            del sessions[session_id]
            return jsonify({"status": "cleaned"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"status": "no session"}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

