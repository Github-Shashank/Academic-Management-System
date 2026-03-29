from flask import Flask
from models import db
from flask import request, jsonify
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Backend Running 🚀"

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    user = User(name=data['name'], role=data['role'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User added"})

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
def post_discussion():
    data = request.json

    discussion = Discussion(
        content=data['content'],
        user_id=data['user_id'],
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
def post_reply():
    data = request.json

    reply = Reply(
        content=data['content'],
        discussion_id=data['discussion_id'],
        user_id=data['user_id']
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

if __name__ == '__main__':
    app.run(debug=True)