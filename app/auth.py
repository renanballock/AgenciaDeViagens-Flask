from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login realizado com sucesso!")
            return redirect(url_for("main.index"))
        else:
            flash("Usuário ou senha inválidos.")
    return render_template("login.html")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form.get("role", "cliente")

        if User.query.filter_by(username=username).first():
            flash("Usuário já existe!")
            return redirect(url_for("auth.register"))

        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Faça login.")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da conta.")
    return redirect(url_for("auth.login"))
