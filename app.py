from flask import Flask, request, jsonify, abort
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventos.db'
app.config['SECRET_KEY'] = 'SDLkjr4j3iLRE325'
db = SQLAlchemy(app)

#Modelos
class Usuarios(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(50), nullable=False)
	apellido = db.Column(db.String(50), nullable=False)
	cedula = db.Column(db.String(8), nullable=False, unique=True)
	correo = db.Column(db.String(100), nullable=False, unique=True)
	token = db.Column(db.String(200))

class Organizadores(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(50), unique=True)
	id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
	usuario = db.relationship('Usuarios', backref=db.backref('organizadores'), lazy=True)

class Eventos(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(100), nullable=False)
	fecha = db.Column(db.String(80), default=datetime.now)
	edad_minima = db.Column(db.Integer, nullable=False)
	id_organizador = db.Column(db.Integer, db.ForeignKey('organizadores.id'))
	organizador = db.relationship('Organizadores', backref=db.backref('eventos', lazy=True))

class Personas(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(50), nullable=False)
	apellido = db.Column(db.String(50), nullable=False)
	cedula = db.Column(db.String(20), nullable=False)
	correo = db.Column(db.String(100), nullable=False)
	fecha_nacimiento = db.Column(db.String(80), nullable=False)
	id_organizador = db.Column(db.Integer, db.ForeignKey('organizadores.id'))
	organizador = db.relationship('Organizadores', backref=db.backref('personas', lazy=True))

class Asistencias(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_evento = db.Column(db.Integer, db.ForeignKey('eventos.id'))
	id_persona = db.Column(db.Integer, db.ForeignKey('personas.id'))
	timestamp_llegada = db.Column(db.DateTime, default=datetime.now)
	evento = db.relationship('Eventos', backref=db.backref('asistencias', lazy=True))
	persona = db.relationship('Personas', backref=db.backref('asistencias', lazy=True))

#Generar Token
def generate_token(id_usuario):
	payload = {
	'id_usuario' : id_usuario,
	'exp' : datetime.utcnow() + timedelta(hours=24)
	}
	token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
	return token

#Verificar Token
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'Authorization' in request.headers:
			token = request.headers['Authorization'].split(" ")[0]
		if not token:
			return jsonify({'message': 'Token Faltante'}), 401
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
			current_user = Usuarios.query.filter_by(id=data['id_usuario']).first()
		except:
			return jsonify({'message': 'token invalido o expirado'}), 401
		return f(current_user, *args, **kwargs)
	return decorated

#Rutas para CREATE
@app.route('/usuarios', methods=['POST'])
def create_usuario():
	data = request.get_json()
	if len(data.get('cedula')) > 8:
		return jsonify({'message': 'cedula excede valor maximo'}), 401
	nuevo_usuario = Usuarios(**data)
	if Usuarios.query.filter_by(cedula=nuevo_usuario.cedula).first() or Usuarios.query.filter_by(correo=nuevo_usuario.correo).first():
		return jsonify({'message': 'Usuario existente'}), 401
	db.session.add(nuevo_usuario)
	db.session.commit()
	token = generate_token(nuevo_usuario.id)
	nuevo_usuario.token = token
	db.session.commit()
	print(token)
	return jsonify({'token':token, 'status': 'exitoso'}), 201

@app.route('/organizadores', methods=['POST'])
@token_required
def create_organizador(current_user):
	data = request.get_json()
	if Organizadores.query.filter_by(nombre=data['nombre']).first():
		return jsonify({'message': 'Organizador ya existe'}), 401
	nuevo_organizador = Organizadores(usuario=current_user, **data)
	db.session.add(nuevo_organizador)
	db.session.commit()
	return jsonify({'id': nuevo_organizador.id, 'status': 'exitoso'}), 201

@app.route('/eventos', methods=['POST'])
@token_required
def create_evento(current_user):
	data = request.get_json()
	id_organizador = data.get('id_organizador')
	organizador = Organizadores.query.get(id_organizador)
	if not organizador:
		return jsonify({'message': 'Organizador no encontrado'}), 404
	if organizador.usuario != current_user:
		return jsonify({'message': 'No autorizado'}), 403
	nuevo_evento = Eventos(organizador=organizador, **data)
	db.session.add(nuevo_evento)
	db.session.commit()
	return jsonify({'id': nuevo_evento.id, 'status': 'exitoso'}), 201

@app.route('/personas', methods=['POST'])
@token_required
def create_persona(current_user):
	data = request.get_json()
	id_organizador = data.get('id_organizador')
	organizador = Organizadores.query.get(id_organizador)
	if len(data.get('cedula')) > 8:
		return jsonify({'message': 'cedula excede valor maximo'}), 401
	if not organizador:
		return jsonify({'message': 'Organizador no encontrado'}), 404
	if organizador.usuario != current_user:
		return jsonify({'message': 'No autorizado'}), 403
	nueva_persona = Personas(organizador=organizador, **data)
	db.session.add(nueva_persona)
	db.session.commit()
	return jsonify({'id': nueva_persona.id, 'status': 'exitoso'}), 201

@app.route('/asistencias', methods=['POST'])
@token_required
def create_asistencia(current_user):
	data = request.get_json()
	id_evento = data.get('id_evento')
	id_persona = data.get('id_persona')
	evento = Eventos.query.get(id_evento)
	persona = Personas.query.get(id_persona)
	if not evento or not persona:
		return jsonify({'message': 'Evento o Persona no encontrados.'}), 404
	nueva_asistencia = Asistencias(evento=evento, persona=persona, **data)
	db.session.add(nueva_asistencia)
	db.session.commit()
	return jsonify({'id': nueva_asistencia.id, 'status': 'exitoso'}), 201

#Rutas para UPDATE
@app.route('/usuarios/<int:id_usuario>', methods=['PUT'])
@token_required
def update_usuario(current_user, id_usuario):
	usuario = Usuarios.query.get(id_usuario)
	if not usuario:
		return jsonify({'message': 'Usuario no encontrado'}), 404
	if current_user.id != usuario.id:
		return jsonify({'message': 'No autorizado'}), 403
	data = request.get_json()
	usuario.nombre = data.get('nombre', usuario.nombre)
	usuario.apellido = data.get('apellido', usuario.apellido)
	usuario.cedula = data.get('cedula', usuario.cedula)
	usuario.correo = data.get('correo', usuario.correo)
	db.session.commit()
	return jsonify({'message': 'Usuario actualizado', 'status': 'exitoso'}), 200

@app.route('/organizadores/<int:id_organizador>', methods=['PUT'])
@token_required
def update_organizador(current_user, id_organizador):
	organizador = Organizadores.query.get(id_organizador)
	if not organizador:
		return jsonify({'message': 'Organizador no encontrado'}), 404
	if organizador.usuario != current_user:
		return jsonify({'message': 'No autorizado'}), 403
	data = request.get_json()
	organizador.nombre = data.get('nombre', organizador.nombre)
	db.session.commit()
	return jsonify({'message': 'Organizador actualizado', 'status': 'exitoso'}), 200

@app.route('/eventos/<int:id_evento>', methods=['PUT'])
@token_required
def update_evento(current_user, id_evento):
    evento = Eventos.query.get(id_evento)
    if not evento:
        return jsonify({'message': 'Evento no encontrado'}), 404
    data = request.get_json()
    evento.nombre = data.get('nombre', evento.nombre)
    evento.fecha = data.get('fecha', evento.fecha)
    evento.edad_minima = data.get('edad_minima', evento.edad_minima)
    db.session.commit()
    return jsonify({'message': 'Evento actualizado'}), 200

@app.route('/personas/<int:id_persona>', methods=['PUT'])
@token_required
def update_persona(current_user, id_persona):
    persona = Personas.query.get(id_persona)
    if not persona:
        return jsonify({'message': 'Persona no encontrada'}), 404
    data = request.get_json()
    persona.nombre = data.get('nombre', persona.nombre)
    persona.apellido = data.get('apellido', persona.apellido)
    persona.cedula = data.get('cedula', persona.cedula)
    persona.correo = data.get('correo', persona.correo)
    persona.fecha_nacimiento = data.get('fecha_nacimiento', persona.fecha_nacimiento)
    db.session.commit()
    return jsonify({'message': 'Persona actualizada'}), 200

@app.route('/asistencias/<int:id_asistencia>', methods=['PUT'])
@token_required
def update_asistencia(current_user, id_asistencia):
    asistencia = Asistencias.query.get(id_asistencia)
    if not asistencia:
        return jsonify({'message': 'Asistencia no encontrada'}), 404
    data = request.get_json()
    asistencia.timestamp_llegada = data.get('timestamp_llegada', asistencia.timestamp_llegada)
    db.session.commit()
    return jsonify({'message': 'Asistencia actualizada'}), 200

# Ruta para DELETE
@app.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
@token_required
def delete_usuario(current_user, id_usuario):
    usuario = Usuarios.query.get(id_usuario)
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado'}), 200

@app.route('/organizadores/<int:id_organizador>', methods=['DELETE'])
@token_required
def delete_organizador(current_user, id_organizador):
    organizador = Organizadores.query.get(id_organizador)
    if not organizador:
        return jsonify({'message': 'Organizador no encontrado'}), 404
    db.session.delete(organizador)
    db.session.commit()
    return jsonify({'message': 'Organizador eliminado'}), 200

@app.route('/eventos/<int:id_evento>', methods=['DELETE'])
@token_required
def delete_evento(current_user, id_evento):
    evento = Eventos.query.get(id_evento)
    if not evento:
        return jsonify({'message': 'Evento no encontrado'}), 404
    db.session.delete(evento)
    db.session.commit()
    return jsonify({'message': 'Evento eliminado'}), 200

@app.route('/personas/<int:id_persona>', methods=['DELETE'])
@token_required
def delete_persona(current_user, id_persona):
    persona = Personas.query.get(id_persona)
    if not persona:
        return jsonify({'message': 'Persona no encontrada'}), 404
    db.session.delete(persona)
    db.session.commit()
    return jsonify({'message': 'Persona eliminada'}), 200

@app.route('/asistencias/<int:id_asistencia>', methods=['DELETE'])
@token_required
def delete_asistencia(current_user, id_asistencia):
    asistencia = Asistencias.query.get(id_asistencia)
    if not asistencia:
        return jsonify({'message': 'Asistencia no encontrada'}), 404
    db.session.delete(asistencia)
    db.session.commit()
    return jsonify({'message': 'Asistencia eliminada'}), 200

# Ruta para RESULT
@app.route('/usuarios', methods=['GET'])
@token_required
def get_usuarios(current_user):
    usuarios = Usuarios.query.all()
    output = []
    for usuario in usuarios:
        usuario_data = {'id': usuario.id, 'nombre': usuario.nombre, 'apellido': usuario.apellido, 'cedula': usuario.cedula, 'correo': usuario.correo}
        output.append(usuario_data)
    return jsonify({'usuarios': output}), 200

@app.route('/organizadores', methods=['GET'])
@token_required
def get_organizadores(current_user):
    organizadores = Organizadores.query.all()
    output = []
    for organizador in organizadores:
        organizador_data = {'id': organizador.id, 'nombre': organizador.nombre, 'id_usuario': organizador.id_usuario}
        output.append(organizador_data)
    return jsonify({'organizadores': output}), 200

@app.route('/eventos', methods=['GET'])
@token_required
def get_eventos(current_user):
    eventos = Eventos.query.all()
    output = []
    for evento in eventos:
        evento_data = {'id': evento.id, 'nombre': evento.nombre, 'fecha': evento.fecha, 'edad_minima': evento.edad_minima, 'id_organizador': evento.id_organizador}
        output.append(evento_data)
    return jsonify({'eventos': output}), 200

@app.route('/personas', methods=['GET'])
@token_required
def get_personas(current_user):
    personas = Personas.query.all()
    output = []
    for persona in personas:
        persona_data = {'id': persona.id, 'nombre': persona.nombre, 'apellido': persona.apellido, 'cedula': persona.cedula, 'correo': persona.correo, 'fecha_nacimiento': persona.fecha_nacimiento, 'id_organizador': persona.id_organizador}
        output.append(persona_data)
    return jsonify({'personas': output}), 200

@app.route('/asistencias', methods=['GET'])
@token_required
def get_asistencias(current_user):
    asistencias = Asistencias.query.all()
    output = []
    for asistencia in asistencias:
        asistencia_data = {'id': asistencia.id, 'id_evento': asistencia.id_evento, 'id_persona': asistencia.id_persona, 'timestamp_llegada': asistencia.timestamp_llegada}
        output.append(asistencia_data)
    return jsonify({'asistencias': output}), 200

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')