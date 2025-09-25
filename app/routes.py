from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import db, Package, Reservation

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    pacotes = Package.query.all()
    return render_template("index.html", pacotes=pacotes, user=current_user)

@bp.route("/packages")
@login_required
def packages():
    pacotes = Package.query.all()
    return render_template("packages.html", pacotes=pacotes, user=current_user)

@bp.route("/packages/add", methods=["POST"])
@login_required
def add_package():
    # 🔹 Somente ADMIN pode adicionar pacotes
    if current_user.role != "admin":
        flash("Apenas administradores podem cadastrar pacotes.")
        return redirect(url_for("main.packages"))

    nome = request.form["nome"]
    destino = request.form["destino"]
    vagas = int(request.form["vagas"])
    preco = float(request.form["preco"])
    p = Package(nome=nome, destino=destino, vagas=vagas, preco=preco)
    db.session.add(p)
    db.session.commit()
    flash("Pacote cadastrado!")
    return redirect(url_for("main.packages"))



@bp.route("/reservations/add", methods=["POST"])
@login_required
def add_reservation():
    # 🔹 Somente CLIENTE pode reservar
    if current_user.role != "cliente":
        flash("Somente clientes podem fazer reservas.")
        return redirect(url_for("main.reservations"))

    cliente = current_user.username
    quantidade = int(request.form["quantidade"])
    pacote_id = int(request.form["pacote_id"])

    pacote = Package.query.get(pacote_id)
    if not pacote:
        flash("Pacote não encontrado!")
        return redirect(url_for("main.reservations"))

    if pacote.vagas < quantidade:
        flash("Não há vagas suficientes!")
        return redirect(url_for("main.reservations"))

    r = Reservation(cliente_nome=cliente, quantidade=quantidade, pacote_id=pacote_id)
    pacote.vagas -= quantidade
    db.session.add(r)
    db.session.commit()
    flash("Reserva registrada!")
    return redirect(url_for("main.reservations"))

@bp.route("/reservations/cancel/<int:res_id>", methods=["POST"])
@login_required
def cancel_reservation(res_id):
    reserva = Reservation.query.get_or_404(res_id)

    if current_user.role == "cliente" and reserva.cliente_nome != current_user.username:
        flash("Você não pode cancelar esta reserva.")
        return redirect(url_for("main.reservations"))

    pacote = Package.query.get(reserva.pacote_id)
    if pacote:
        pacote.vagas += reserva.quantidade

    db.session.delete(reserva)
    db.session.commit()
    flash("Reserva cancelada com sucesso!")
    return redirect(url_for("main.reservations"))


@bp.route("/reservations")
@login_required
def reservations():
    # Admin vê todas, cliente só suas próprias
    if current_user.role == "admin":
        reservas = Reservation.query.all()
    else:
        reservas = Reservation.query.filter_by(cliente_nome=current_user.username).all()
    return render_template("reservations.html", reservas=reservas, user=current_user)


@bp.route("/reservations/edit/<int:res_id>", methods=["GET", "POST"])
@login_required
def edit_reservation(res_id):
    reserva = Reservation.query.get_or_404(res_id)

    # Controle de acesso
    if current_user.role == "cliente" and reserva.cliente_nome != current_user.username:
        flash("Você não pode editar esta reserva.")
        return redirect(url_for("main.reservations"))

    if request.method == "POST":
        nova_quantidade = int(request.form["quantidade"])
        pacote = Package.query.get(reserva.pacote_id)
        if not pacote:
            flash("Pacote não encontrado!")
            return redirect(url_for("main.reservations"))

        # Ajusta vagas do pacote
        diferenca = nova_quantidade - reserva.quantidade
        if pacote.vagas < diferenca:
            flash("Não há vagas suficientes para atualizar a reserva.")
            return redirect(url_for("main.reservations"))

        pacote.vagas -= diferenca
        reserva.quantidade = nova_quantidade
        db.session.commit()
        flash("Reserva atualizada!")
        return redirect(url_for("main.reservations"))

    return render_template("edit_reservation.html", reserva=reserva)
