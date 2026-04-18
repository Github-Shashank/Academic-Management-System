import os
import uuid
import jwt
import time
from functools import wraps
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import request, jsonify, Flask
from models import *
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

rate_limit_store = {}

from functools import wraps

def rate_limit(max_requests, window_seconds):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = None

            # try getting user from JWT
            if 'Authorization' in request.headers:
                token = request.headers['Authorization']
                try:
                    data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                    user_id = data['user_id']
                except:
                    user_id = request.remote_addr
            else:
                user_id = request.remote_addr

            key = f"{user_id}:{f.__name__}"
            current_time = time.time()

            if key not in rate_limit_store:
                rate_limit_store[key] = []

            # remove old requests
            rate_limit_store[key] = [
                t for t in rate_limit_store[key]
                if current_time - t < window_seconds
            ]

            if len(rate_limit_store[key]) >= max_requests:
                return {
                    "error": "Too many requests",
                    "retry_after_seconds": window_seconds
                }, 429

            rate_limit_store[key].append(current_time)

            return f(*args, **kwargs)

        return wrapped
    return decorator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg' # } # txt is for testing only
                      , 'txt'} # should be removed for final production

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# create folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Backend Running 🚀"

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    hashed_password = generate_password_hash(data['password'])

    user = User(
        name=data['name'],
        role=data['role'],
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return {"message": "User registered"}

@app.route('/login', methods=['POST'])
@rate_limit(5, 60) 
def login():
    data = request.json

    user = User.query.filter_by(name=data['name']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return {"error": "Invalid credentials"}, 401

    token = jwt.encode({
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return {
        "message": "Login successful",
        "token": token
    }

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return {"error": "Token missing"}, 401

            parts = auth_header.split()

            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
            else:
                return {"error": "Invalid token format"}, 401

        if not token:
            return {"error": "Token missing"}, 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/add_subject', methods=['POST'])
def add_subject():
    data = request.json

    subject = Subject(name=data['name'])
    db.session.add(subject)
    db.session.commit()

    return {"message": "Subject added"}

@app.route('/add_lecture', methods=['POST'])
def add_lecture():
    data = request.json

    lecture = Lecture(
        title=data['title'],
        lecture_no=data['lecture_no'],
        subject_id=data['subject_id'],
        file_url=data.get('file_url', '')
    )

    db.session.add(lecture)
    db.session.commit()

    return {"message": "Lecture added"}

@app.route('/get_lectures/<int:subject_id>', methods=['GET'])
def get_lectures(subject_id):
    lectures = Lecture.query.filter_by(subject_id=subject_id)\
        .order_by(Lecture.lecture_no).all()

    result = []
    for lec in lectures:
        result.append({
            "id": lec.id,
            "title": lec.title,
            "lecture_no": lec.lecture_no,
            "file_url": lec.file_url
        })

    return result

@app.route('/post_discussion', methods=['POST'])
def post_discussion(current_user):
    data = request.json

    discussion = Discussion(
        content=data['content'],
        user_id=current_user.id,
        subject_id=data['subject_id'],
        lecture_id=data['lecture_id']
    )

    db.session.add(discussion)
    db.session.commit()

    return {"message": "Discussion posted"}

@app.route('/get_discussions/<int:lecture_id>', methods=['GET'])
def get_discussions(lecture_id):
    discussions = Discussion.query.filter_by(lecture_id=lecture_id).all()

    result = []
    for d in discussions:
        result.append({
            "id": d.id,
            "content": d.content,
            "user_id": d.user_id
        })

    return result

@app.route('/post_reply', methods=['POST'])
def post_reply(current_user):
    data = request.json

    reply = Reply(
        content=data['content'],
        discussion_id=data['discussion_id'],
        user_id=current_user.id
    )

    db.session.add(reply)
    db.session.commit()

    return {"message": "Reply added"}

@app.route('/get_replies/<int:discussion_id>', methods=['GET'])
def get_replies(discussion_id):
    replies = Reply.query.filter_by(discussion_id=discussion_id).all()

    result = []
    for r in replies:
        result.append({
            "id": r.id,
            "content": r.content,
            "user_id": r.user_id
        })

    return result

@app.route('/create_assignment', methods=['POST'])
def post_assignment(current_user):
    data = request.json

    assignment =  Assignment(
        title = data['title'],
        description = data['description'],
        subject_id = data['subject_id'],
        created_by = current_user.id,
        deadline = datetime.strptime(data['deadline'], "%Y-%m-%d %H:%M:%S")
    )   

    db.session.add(assignment)
    db.session.commit()

    return {"message":"assignment posted"}

@app.route('/get_assignment/<int:subject_id>', methods=['GET'])
def get_assignment(subject_id):
    assignments = Assignment.query.filter_by(subject_id=subject_id).all()

    result = []
    for a in assignments:
        result.append({
            "id":a.id,
            "title":a.title,
            "description":a.description,
            "subject_id":a.subject_id,
            "created_by":a.created_by,
            "deadline": a.deadline.strftime("%Y-%m-%d %H:%M:%S")
        })

    return result

@app.route('/submit_assignment', methods=['POST'])
@token_required
@rate_limit(3, 60)
def submit_assignment(current_user):
    data = request.json

    # 🔹 Validate assignment exists
    assignment = Assignment.query.get(data['assignment_id'])
    if not assignment:
        return {"error": "Assignment not found"}, 404

    if current_user.role != "student":
        return {"error": "Only students can submit"}, 403

    try:
        submission = Submissions(
            assignment_id=data['assignment_id'],
            student_id=current_user.id,
            file_url=data['file_url'],
            submitted_at=datetime.now()
        )

        db.session.add(submission)
        db.session.commit()

        return {"message": "Assignment submitted"}

    except Exception as e:
        db.session.rollback()
        return {"error": "Already submitted or invalid data"}

@app.route('/get_submissions/<int:assignment_id>', methods=['GET'])
def get_submissions(assignment_id):
    submissions = Submissions.query.filter_by(assignment_id=assignment_id).all()

    result = []
    for s in submissions:
        result.append({
            "id": s.id,
            "assignment_id": s.assignment_id,
            "student_id": s.student_id,
            "file_url": s.file_url,
            "submitted_at": s.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return result

@app.route('/upload_file', methods=['POST'])
@rate_limit(3, 60)
def upload_file():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files['file']

    if file.filename == '':
        return {"error": "Empty filename"}, 400

    if not allowed_file(file.filename):
        return {"error": "File type not allowed"}, 400

    # secure filename
    filename = secure_filename(file.filename)

    # add UUID to avoid overwrite
    unique_filename = str(uuid.uuid4()) + "_" + filename

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    file.save(filepath)

    # return clean URL path
    return {
        "message": "File uploaded",
        "file_url": f"uploads/{unique_filename}"
    }

@app.route('/files/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# @app.route('get_my_submissions/<int:student_id>', methods=['GETS'])
# def get_my_submissions(student_id):

if __name__ == '__main__':
    app.run(debug=True)