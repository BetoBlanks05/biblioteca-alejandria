from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify,render_template_string
from base import db, Usuario
from werkzeug.security import generate_password_hash, check_password_hash
import re, jwt, datetime, base64
from functools import wraps

SECRET_KEY = 'odi0UvM3'

views = Blueprint('views', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_base64 = request.headers.get('x-access-token')
        if not token_base64:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Decode token from base64
            token = base64.b64decode(token_base64).decode()
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = Usuario.query.filter_by(id_usuario=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(current_user, *args, **kwargs)
    return decorated

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.password, password):
            # Generate token
            token = jwt.encode({
                'user_id': usuario.id_usuario,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')

            # Encode token in base64
            token_base64 = base64.b64encode(token.encode()).decode()

            flash('Inicio de sesión exitoso.', 'success')
            return jsonify({'token': token_base64})
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')

@views.route('/')
def start():
    return render_template('start.html')

@views.route('/robots.txt')
def robots():
    return render_template_string('''
    {% extends "layout.html" %}

    {% block content %}
        <div class="container text-center mt-5">
            <h1 class="display-3 fw-bold text-success">¡Felicidades metiche!</h1>
            <h2 class="display-5 text-primary">Encontraste una flag:</h2>

            <!-- Contenedor adicional para centrar más la flag -->
            <div class="d-flex justify-content-center align-items-center mt-4">
                <h2 class="display-12 text-primary">
                    YULEEON_ctf{¿Bu5c45_vUlneRAbIlIdAdEs_M3j0r_h4z_un_sc4n_4_tU_4atuEst1m4_tE_h4cE_f4LtA_3Res_f4c1l_c0m0_uN_MD5}
                </h2>
            </div>

            <img src="{{ url_for('static', filename='images/robot.jpeg') }}" alt="Flag" class="img-fluid mt-4" style="max-width: 300px;">
        </div>
    {% endblock %}
    ''')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/payment')
def index():
    return render_template('payment.html')

@views.route('/forgetpassw')
def forgetpassw():
    return render_template('forgetpassw.html')

@views.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        correo = request.form.get('correo')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('views.registro'))

        usuario_existente = Usuario.query.filter_by(correo=correo).first()
        if usuario_existente:
            flash('El correo ya está registrado.', 'danger')
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            nuevo_usuario = Usuario(nombre=nombre, apellidos=apellidos, correo=correo, password=hashed_password)
            db.session.add(nuevo_usuario)
            db.session.commit()

            # Generate token
            token = jwt.encode({
                'user_id': nuevo_usuario.id_usuario,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')

            # Encode token in base64
            token_base64 = base64.b64encode(token.encode()).decode()

            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return jsonify({'token': token_base64})

    return render_template('registro.html')

@views.route('/buy_book', methods=['POST'])
@token_required
def buy_book(current_user):
    datos = request.json
    book_id = datos.get('book_id')

    # Simulate the process of buying a book
    # In a real application, you would check if the book is available, process the payment, etc.
    if not book_id:
        return jsonify({'message': 'Book ID is missing!'}), 400

    # Simulate a successful purchase
    return jsonify({'message': f'Book with ID {book_id} purchased successfully by user {current_user.nombre}!'})

# Payment validation functions and route
def validar_tarjeta(numero):
    """Valida que el número de tarjeta tenga 16 dígitos numéricos."""
    return re.fullmatch(r"\d{16}", numero) is not None

def validar_fecha_expiracion(mes, anio):
    """Verifica que la fecha de expiración sea válida y no esté vencida."""
    hoy = datetime.datetime.now()
    try:
        mes = int(mes)
        anio = int(anio)
        if anio < hoy.year or (anio == hoy.year and mes < hoy.month):
            return False, "Error: La tarjeta está vencida"
        if not (1 <= mes <= 12):
            return False, "Error: El mes ingresado no es válido"
        return True, ""
    except ValueError:
        return False, "Error: Fecha de expiración inválida"

def validar_cvv(cvv):
    """Valida que el CVV tenga 3 o 4 dígitos numéricos."""
    return re.fullmatch(r"\d{3,4}", cvv) is not None

@views.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    datos = request.json
    numero_tarjeta = datos.get('numero_tarjeta')
    mes_expiracion = datos.get('mes_expiracion')
    anio_expiracion = datos.get('anio_expiracion')
    cvv = datos.get('cvv')

    if not validar_tarjeta(numero_tarjeta):
        return jsonify({'mensaje': 'Error: Número de tarjeta inválido'}), 400

    fecha_valida, mensaje_fecha = validar_fecha_expiracion(mes_expiracion, anio_expiracion)
    if not fecha_valida:
        return jsonify({'mensaje': mensaje_fecha}), 400

    if not validar_cvv(cvv):
        return jsonify({'mensaje': 'Error: CVV inválido'}), 400

    return jsonify({'mensaje': 'Pago exitoso'})