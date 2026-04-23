from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellidos = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.nombre} - {self.correo}>'

class Editorial(db.Model):
    __tablename__ = 'editorial'
    
    id_editorial = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_libro = db.Column(db.Integer, db.ForeignKey('libro.id_libro'))
    fecha = db.Column(db.Date)
    pais = db.Column(db.Integer)  # Puede ser una referencia a una tabla de países o solo un valor numérico
    
    # Relación con la tabla "libro"
    libro = db.relationship('Libro', backref=db.backref('editoriales', lazy=True))
    
    def __repr__(self):
        return f'<Editorial {self.id_editorial} - {self.fecha}>'

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_categoria = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Categoria {self.nombre_categoria}>'

    
   

class Pago(db.Model):
    __tablename__ = 'pago'
    
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    monto = db.Column(db.Numeric(10,2))
    metodo_pago = db.Column(db.String(50))
    fecha_pago = db.Column(db.Date)
    
    # Relación con la tabla "usuario"
    usuario = db.relationship('Usuario', backref=db.backref('pagos', lazy=True))
    
    def __repr__(self):
        return f'<Pago {self.id_pago} - {self.monto} - {self.metodo_pago}>'

class Administracion(db.Model):
    __tablename__ = 'administracion'
    
    id_administracion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), unique=True)
    nivel_acceso = db.Column(db.Integer)
    
    # Relación con la tabla "usuario"
    usuario = db.relationship('Usuario', backref=db.backref('administraciones', lazy=True))
    
    def __repr__(self):
        return f'<Administracion {self.id_usuario} - Nivel {self.nivel_acceso}>'

class Libro(db.Model):
    __tablename__ = 'libro'
    
    id_libro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100))
    genero = db.Column(db.String(100))
    editorial = db.Column(db.String(100))
    isbn = db.Column(db.Integer, unique=True)
    año_publicacion = db.Column(db.Date)
    disponibilidad = db.Column(db.Integer)
    
    def __repr__(self):
        return f'<Libro {self.titulo} - {self.autor}>'
