[Link:https://jonathan26.pythonanywhere.com](https://jonathan26.pythonanywhere.com)


Token
Al crear usuario se devuelve un Token para realizar operaciones sobre la API.
Se debe pasar en Header como valor del parametro Authorization en todas las operaciones.

[Endpoints]
/usuarios
Parametros
  {
    "nombre": "<valor>",
    "apellido": "<valor>",
    "cedula": "<valor>",
    "correo": "<valor>",
  }
Devuelve
al crear usuario se devuelve un Token para realizar operaciones sobre la API.

/organizadores
Header
  Authorization: <TOKEN>
Parametros
  {
    "nombre": "<valor>",
    "id_usuario": "<valor>"
  }
Devuelve
al crear Organizador se devuelve su ID.

/eventos
Header
  Authorization: <TOKEN>
Parametros
  {
    "nombre": "<valor>",
    "fecha": "<valor>",
    "edad_minima": "<valor>",
    "id_organizador": "<valor>"
  }
Devuelve
al crear Eventos se devuelve su ID.

/personas
Parametros
  {
    "nombre": "<valor>",
    "apellido": "<valor>",
    "cedula": "<valor>",
    "correo": "<valor>",
    "fecha_nacimiento": "<valor>",
    "id_organizador": "<valor>"
  }
Devuelve
al crear Persona se devuelve el ID.

/asistencias
Parametros
  {
    "id_evento": "<valor>",
    "id_persona": "<valor>"
  }
Devuelve
al crear Asistencia se devuelve el ID.

Para insertar o modificar se deben enviar parametros dentro de un json.

[Comandos]
POST: CREATE/INSERT
  Se pasan parametros dentro de un json con el token de Authorization
GET: RESULT/SELECT
  Solo se ejecuta un get con el token de Authorization. Sin otros parametros
PUT: UPDATE
  Se pasan parametros que se quieren modificar dentro de un json con el token de Authorization
DELETE: DELETE
  Se coloca al final del link el id del registro a eliminar. por ejemplo: https://jonathan26.pythonanywhere.com/asistencias/1
