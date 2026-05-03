from flask import Blueprint, request, jsonify
from models import db, Admin, Opportunity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from itsdangerous import URLSafeTimedSerializer
from flask import render_template

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('admin.html')

@main.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    if Admin.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed = generate_password_hash(password)

    user = Admin(full_name=name, email=email, password_hash=hashed)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Signup successful"})

@main.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = Admin.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user)

    return jsonify({
        "message": "Login successful",
        "name": user.full_name
    })

@main.route('/api/forgot-password', methods=['POST'])
def forgot():
    data = request.get_json()
    email = data.get('email')

    user = Admin.query.filter_by(email=email).first()

    serializer = URLSafeTimedSerializer("secret")

    if user:
        token = serializer.dumps(email, salt='reset')
        print(f"Reset link: http://localhost:5000/reset/{token}")
    else:
        print("Email not found in DB")

    return jsonify({"message": "If email exists, link sent"})

@main.route('/api/opportunities', methods=['GET'])
@login_required
def get_ops():
    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()

    data = []
    for op in ops:
        data.append({
            "id": op.id,
            "name": op.name,
            "category": op.category,
            "description": op.description
        })

    return jsonify(data)

@main.route('/api/opportunities', methods=['POST'])
@login_required
def create_op():
    data = request.get_json()

    op = Opportunity(
        name=data['name'],
        category=data['category'],
        description=data['description'],
        admin_id=current_user.id
    )

    db.session.add(op)
    db.session.commit()

    return jsonify({"message": "Created"})

@main.route('/api/opportunities/<int:id>', methods=['DELETE'])
@login_required
def delete_op(id):
    op = Opportunity.query.get(id)

    if op.admin_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(op)
    db.session.commit()

    return jsonify({"message": "Deleted"})
