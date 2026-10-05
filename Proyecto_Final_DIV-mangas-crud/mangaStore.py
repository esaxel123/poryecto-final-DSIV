#librerias necesarias para el funcionamiento del backend
from flask import Flask, jsonify, request
from flask_cors import CORS #permite que el frontend pueda hacer peticiones a este backend sin problemas de CORS
import sqlite3
from datetime import datetime#importamos la libreria datetime para poder guardar la fecha y hora de las ventas en la base de datos

app = Flask(__name__)

CORS(app)#habilitamos CORS para permitir que el frontend pueda hacer peticiones a este backend sin problemas de CORS
#para que no ordene por alfabeto los datos del json y mantenga el orden que designamos
app.json.sort_keys = False
database = "mangaStore1.db" #nombre de la base de datos

def conexionDB(): #definimos un metodo para conectarnos a la base de datos
    return sqlite3.connect(database) #en caso de que la base de datos no exista sqlite3 la creara

# metodo para la creacion de los campos de la base de datos
def inicializarDB():
    try:
        conn = conexionDB() #abre la conexion a la base de datos
        cursor = conn.cursor() #crea un cursor para ejecutar las concultas

        # Habilitar llaves foráneas a nivel de base de datos
        cursor.execute("PRAGMA foreign_keys = ON;")

        # ejecutamos la conculta que creara los campos de nuestra base de datos
        
        #crear tabla editoriales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS editoriales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                pais TEXT NOT NULL
            )
        """)
        
        #crear tabla mangas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mangas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                volumen INTEGER NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                id_editorial INTEGER,
                FOREIGN KEY(id_editorial) REFERENCES editoriales(id)
            )
        """)

        #crear tabla ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                metodo_pago TEXT CHECK(metodo_pago IN ('Efectivo', 'Tarjeta')) NOT NULL 
            )
        """)

        #crear tabla detalle_ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                manga_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                FOREIGN KEY(venta_id) REFERENCES ventas(id),
                FOREIGN KEY(manga_id) REFERENCES mangas(id)
            )
        """)
        
        # Crear tabla de imágenes relacionada
        cursor.execute("""
           CREATE TABLE IF NOT EXISTS manga_imagenes (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           manga_id INTEGER NOT NULL,
          url_imagen TEXT NOT NULL,
           FOREIGN KEY(manga_id) REFERENCES mangas(id) ON DELETE CASCADE
    )
""")

        conn.commit() #guarda los cambios realizados en la base de datos
        conn.close()#cierra la conexion a la base de datos
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")



#VISUALIZAR TODOS LOS MANGAS, METODO GET
@app.route("/mangas", methods=["GET"]) 
def obtenerTodos():
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.titulo, m.autor, m.volumen, m.precio, m.stock, e.nombre, i.url_imagen
            FROM mangas m
            LEFT JOIN manga_imagenes i ON m.id = i.manga_id
            LEFT JOIN editoriales e ON m.id_editorial = e.id
        """) #ejecuta la consulta mySQL para seleccionar todos los registros de la base de datos
        filas = cursor.fetchall() #guarda todos los datos obtenidos de la consulta
        
        #covertimos cada fila de la base de datos (la cual es una tupla) en un diccionario de python
        mangas = []
        for f in filas:
            mangas.append({
                "id": f[0],
                "titulo": f[1],
                "autor": f[2], 
                "volumen": f[3],
                "precio": f[4],
                "stock": f[5],
                "id_editorial": f[6],
                "url_imagen": f[7]
            })
        
        conn.close() #cierra la conexion a la base de datos
        return jsonify(mangas), 200 #envia la lista al usuario en formato JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#VISUALIZAR MANGA POR ID, METODO GET
@app.route("/mangas/<int:id>", methods=["GET"])
def obtenerUno(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.id, m.titulo, m.autor, m.volumen, m.precio, m.stock, e.nombre, i.url_imagen
            FROM mangas m
            LEFT JOIN manga_imagenes i ON m.id = i.manga_id
            LEFT JOIN editoriales e ON m.id_editorial = e.id
            WHERE m.id = ?
        """, (id,)) #ejecuta la consulta mySQL para seleccionar el registro que coincida con el id ingresado por el usuario
        fila = cursor.fetchone() # fetchone guardara el primer datos que coincida con la consulta
        conn.close()

        # Si "fila" tiene contenido, crearemos el JSON
        if fila:
            manga = {
                "id": fila[0], 
                "titulo": fila[1], 
                "autor": fila[2], 
                "volumen": fila[3], 
                "precio": fila[4], 
                "stock": fila[5],
                "id_editorial": fila[6],
                "url_imagen": fila[7]
            }
            return jsonify(manga), 200 #consulta exitosa
        
        # Si no se encuentra el id devolvera un mensaje de error
        return jsonify({"error": "Manga no encontrado"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
@app.route("/mangas/nombre/<string:nombre>", methods=["GET"])
def MangaporNombre(nombre):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
       
        cursor.execute("""
            SELECT m.id, m.titulo, m.autor, m.volumen, m.precio, m.stock, e.nombre, i.url_imagen
            FROM mangas m
            LEFT JOIN manga_imagenes i ON m.id = i.manga_id
            LEFT JOIN editoriales e ON m.id_editorial = e.id
            WHERE m.titulo LIKE ?
        """, (f"%{nombre}%",)) 
        
        filas = cursor.fetchall() # Usamos fetchall para obtener TODOS los que coincidan
        conn.close()

        # Transformamos todas las filas en una lista de diccionarios
        mangas = []
        for fila in filas:
            mangas.append({
                "id": fila[0], 
                "titulo": fila[1], 
                "autor": fila[2], 
                "volumen": fila[3], 
                "precio": fila[4], 
                "stock": fila[5],
                "id_editorial": fila[6],
                "url_imagen": fila[7]
            })
        
        # Siempre devolvemos la lista, incluso si está vacía []
        return jsonify(mangas), 200 
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#VISUALIZAR MANGA POR AUTOR, METODO GET
    
@app.route("/mangas/autor/<string:autor>", methods=["GET"])
def MangaporAutor(autor):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
       
        cursor.execute("""
            SELECT m.id, m.titulo, m.autor, m.volumen, m.precio, m.stock, e.nombre, i.url_imagen
            FROM mangas m
            LEFT JOIN manga_imagenes i ON m.id = i.manga_id
            LEFT JOIN editoriales e ON m.id_editorial = e.id
            WHERE m.autor LIKE ? 
        """, (f"%{autor}%",)) 
        
        filas = cursor.fetchall() # Usamos fetchall para obtener TODOS los que coincidan
        conn.close()

        # Transformamos todas las filas en una lista de diccionarios
        mangas = []
        for fila in filas:
            mangas.append({
                "id": fila[0], 
                "titulo": fila[1], 
                "autor": fila[2], 
                "volumen": fila[3], 
                "precio": fila[4], 
                "stock": fila[5],
                "id_editorial": fila[6],
                "url_imagen": fila[7]
            })
        
        # Siempre devolvemos la lista, incluso si está vacía []
        return jsonify(mangas), 200 
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
#INSERTAR NUEVO MANGA, METODO POST
@app.route("/mangas", methods=["POST"])
def insertar():
    try:
        data = request.json #trae los datos insertados por el usuario
        
        #validaciones basicas
        campos_obligatorios = ["titulo", "autor", "volumen", "precio", "stock", "id_editorial"]
        
        # Revisar que todos los campos existan en el JSON y no sean None o esten vacios
        for campo in campos_obligatorios:
            if campo not in data or data[campo] is None or data[campo] == "":
                return jsonify({"error": f"El campo '{campo}' es obligatorio y no puede ser nulo"}), 400 #mensaje de error de que falto llenar un campo
            
        # Validación de tipos y valores numéricos
        if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
            return jsonify({"error": "El precio debe ser un número positivo"}), 400
        if not isinstance(data["stock"], int) or data["stock"] < 0:
            return jsonify({"error": "El stock debe ser un número entero positivo"}), 400
        if not isinstance(data["volumen"], (int, float)):
            return jsonify({"error": "El volumen debe ser un número "}), 400
        
        conn = conexionDB()
        cursor = conn.cursor()

        # Evitar duplicados por título
        cursor.execute("SELECT id FROM mangas WHERE titulo = ? AND volumen = ?", (data["titulo"], data["volumen"]))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Este manga y volumen ya están registrados"}), 409

        # Verificamos la existencia de editorial
        cursor.execute("SELECT id FROM editoriales WHERE id = ?", (data["id_editorial"],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "La editorial no existe"}), 404
        
        cursor.execute("""
            INSERT INTO mangas (titulo, autor, volumen, precio, stock, id_editorial) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data["titulo"], data["autor"], data["volumen"], data["precio"], data["stock"], data["id_editorial"]))
        
        conn.commit() #guarda los ccambios
        nuevo_id = cursor.lastrowid #nos permite saber el nuevo id que le asigno la base de datos al nuevo producto que agregamos
        conn.close()
        return jsonify({"mensaje": "Manga registrado correctamente", "id": nuevo_id}), 201 #mensaje de que el manga se agrego correctamente
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#ACTUALIZAR MANGA, METODO PUT
@app.route("/mangas/<int:id>", methods=["PUT"])
def actualizar(id):
    try:
        data = request.json #obtiene los datos insertados por el usuario
        
        #validaciones basicas para actualizar
        campos_obligatorios = ["titulo", "autor", "volumen", "precio", "stock", "id_editorial"]
        # Revisar que todos los campos existan en el JSON y no sean None o esten vacios
        for campo in campos_obligatorios:
            if campo not in data or data[campo] is None or data[campo] == "":
                return jsonify({"error": f"Para actualizar, el campo '{campo}' no puede ser nulo"}), 400
            
         # Validación de tipos y valores numéricos
        if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
            return jsonify({"error": "El precio debe ser un número positivo"}), 400
        if not isinstance(data["stock"], int) or data["stock"] < 0:
            return jsonify({"error": "El stock debe ser un número entero positivo"}), 400
        if not isinstance(data["volumen"], (int, float)):
            return jsonify({"error": "El volumen debe ser un número "}), 400
        
        conn = conexionDB()
        cursor = conn.cursor()

        # Evitar duplicados por título
        cursor.execute("SELECT id FROM mangas WHERE titulo = ? AND volumen = ? AND id != ?", (data["titulo"], data["volumen"], id))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Este manga y volumen ya están registrados"}), 409

        # Verificamos la existencia de editorial
        cursor.execute("SELECT id FROM editoriales WHERE id = ?", (data["id_editorial"],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "La editorial no existe"}), 404
        
        cursor.execute("SELECT * FROM mangas WHERE id = ?", (id,))
        if not cursor.fetchone(): #si no existe manda un mensaje de error
            conn.close()
            return jsonify({"error": "Manga no encontrado"}), 404

        #si si existe actualizara la informacion de los campos por los datos que haya ingresado el usuario
        cursor.execute("""
            UPDATE mangas 
            SET titulo = ?, autor = ?, volumen = ?, precio = ?, stock = ?, id_editorial = ?
            WHERE id = ?
        """, (data["titulo"], data["autor"], data["volumen"], data["precio"], data["stock"], data["id_editorial"], id))
        
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Manga actualizado con éxito"}), 200 #mensaje de que se actualizo correctamente
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#ELIMINAR MANGA, METODO DELETE
@app.route("/mangas/<int:id>", methods=["DELETE"])
def eliminar(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        #ejecuta la consulta SQL para eliminar el producto que coincida con el id ingresado por el usuario
        cursor.execute("DELETE FROM mangas WHERE id = ?", (id,))
        conn.commit() #guarda los cambios
        
        if cursor.rowcount == 0: #cuenta el numero de fila afectada por la ultima consulta, si es cero el id no se encontro
            conn.close()
            return jsonify({"error": "ID no encontrado"}), 404
            
        conn.close()
        return jsonify({"mensaje": "Manga eliminado"}), 200 #si no, el manga fue eliminado
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    #RUTAS PARA EDITORIALES Y VENTAS, SEGUIRAN LA MISMA LOGICA QUE LAS RUTAS DE MANGAS, SOLO CAMBIANDO LOS CAMPOS Y EL NOMBRE DE LA TABLA EN LAS CONSULTAS SQL
    # --- CRUD PARA EDITORIALES ---

@app.route("/editoriales", methods=["GET"])
def obtenerEditoriales():
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM editoriales") #se seleccionan todos los registros de la tabla "editoriales"
        filas = cursor.fetchall()
        
        editoriales = [{"id": f[0], "nombre": f[1], "pais": f[2]} for f in filas] #acomodamos los resultados en una lista de diccionarios para cada registro
        
        conn.close()
        return jsonify(editoriales), 200 #regresamos la lista en formato json
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/editoriales/<int:id>", methods=["GET"])
def obtenerEditorialesId(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM editoriales WHERE id = ?", (id,)) #se selecciona el registro que coincida con el id ingresado
        fila = cursor.fetchone()
        
        editoriales = {"id": fila[0], "nombre": fila[1], "pais": fila[2]} #acomodamos los resultados en un diccionario
        
        conn.close()
        return jsonify(editoriales), 200 #regresamos los resultados en formato json
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/editoriales/nombre/<string:nombre>", methods=["GET"])
def obtenerEditorialesNom(nombre):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM editoriales WHERE LOWER(nombre) LIKE LOWER(?)", (f"%{nombre}%",)) #se selecciona el registro que coincida con el id ingresado
        fila = cursor.fetchone()

        if not fila:
            return jsonify({
                "mensaje" : "No se encontro la editorial"
            }),400
        
        editoriales = {"id": fila[0], "nombre": fila[1], "pais": fila[2]} #acomodamos los resultados en un diccionario
        
        conn.close()
        return jsonify(editoriales), 200 #regresamos los resultados en formato json
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

#edpoint para buscar por pais

@app.route("/editoriales/pais/<string:pais>", methods=["GET"])
def obtenerEditorialesPais(pais):
    try:
        conn = conexionDB()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM editoriales WHERE LOWER(pais) LIKE LOWER(?)",(f"%{pais}%",)
        )

        filas = cursor.fetchall()

        if not filas:
            return jsonify({
                "mensaje": "No se encontraron editoriales"
            }), 404

        editoriales = []

        for fila in filas:
            editoriales.append({
                "id": fila[0],
                "nombre": fila[1],
                "pais": fila[2]
            })

        conn.close()
        return jsonify(editoriales), 200 #regresamos los resultados en formato json
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    

@app.route("/editoriales", methods=["POST"])
def insertarEditorial():
    try:
        data = request.json #obtenemos los datos insertados popr el usuario
        if "nombre" not in data or "pais" not in data: #si el nombre o pais no se encuentran lanza un mensaje de error, estos campos son obligatorios
            return jsonify({"error": "Los campos 'nombre' y 'pais' son obligatorios"}), 400

        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO editoriales (nombre, pais) VALUES (?, ?)", (data["nombre"], data["pais"])) #insertamos en la tabla la nueva editorial
        conn.commit()
        nuevo_id = cursor.lastrowid #obtenemos el id que la base de datos le asigno a la editorial que agregamos
        conn.close()
        
        return jsonify({"mensaje": "Editorial registrada", "id": nuevo_id}), 201 #mensaje de que se agrego exitosamente
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/editoriales/<int:id>", methods=["PUT"])
def actualizarEditorial(id):
    try:
        data = request.json
        if "nombre" not in data or "pais" not in data:
            return jsonify({"error": "Los campos 'nombre' y 'pais' son obligatorios"}), 400

        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("UPDATE editoriales SET nombre = ?, pais = ? WHERE id = ?", (data["nombre"], data["pais"], id)) #actualizamos la editorial con los datos ingresado por el usuario
        conn.commit()
        
        #si ninguna fila fue afectada significa que el id de la editorial no se encontro
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Editorial no encontrada"}), 404
            
        conn.close()
        return jsonify({"mensaje": "Editorial actualizada"}), 200 #mensaje de que si se pudo actualizar correctamente
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/editoriales/<int:id>", methods=["DELETE"])
def eliminarEditorial(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()

        # Integridad referencial: No borrar si tiene mangas
        cursor.execute("SELECT COUNT(*) FROM mangas WHERE id_editorial = ?", (id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({"error": "No se puede eliminar: existen mangas asociados a esta editorial"}), 400
        
        cursor.execute("DELETE FROM editoriales WHERE id = ?", (id,)) #elimina la editorial que coincida con el id ingresado
        conn.commit()
        
         #si ninguna fila fue afectada significa que el id de la editorial no se encontro
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Editorial no encontrada"}), 404
            
        conn.close()
        return jsonify({"mensaje": "Editorial eliminada"}), 200 #mensaje de que se elimino la editorial exitosamente
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#CRUD PARA VENTAS
    
#GET ventas
@app.route("/ventas", methods=["GET"])
def obtenerVentas():
    try:
        conn = conexionDB()
        cursor = conn.cursor()

        #obtenemos todos los detalles de la venta
        cursor.execute("""
            SELECT v.id, v.fecha, v.total,v.metodo_pago, m.titulo, d.cantidad, d.precio_unitario
            FROM ventas v
            JOIN detalle_ventas d ON v.id = d.venta_id
            JOIN mangas m ON d.manga_id = m.id
            ORDER BY v.id DESC
        """)
        filas = cursor.fetchall()
        conn.close()

        #creamos un diccionario para agrupar las ventas por su id
        ventas_agrupadas = {}

        #ciclo for para recorrer cada fila de nuestra consulta
        for f in filas:
            id_venta = f[0]
            
            #si el id de la venta no esta en el diccionario entonces se agrega
            if id_venta not in ventas_agrupadas:
                ventas_agrupadas[id_venta] = {
                    "id_venta": id_venta,
                    "fecha": f[1],
                    "total_pagado": f[2],
                    "metodo_pago": f[3],
                    "articulos": [] #lista donde se guardaran todos los mangas de la venta y dus detalles
                }
            
            #aqui agregamos los mangas y sus detalles a la lista articulos
            ventas_agrupadas[id_venta]["articulos"].append({
                "manga": f[4],
                "cantidad": f[5],
                "precio_unitario": f[6],
                "subtotal": f[5] * f[6]
            })

        #transformamos los valores del diccionario a una lista para que nos la regrese en json
        return jsonify(list(ventas_agrupadas.values())), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#GET ventas por id
@app.route("/ventas/<int:id>", methods=["GET"])
def obtenerVentaPorId(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        
        #consulta que nos traer el id de la venta que coincida con la busqueda
        cursor.execute("SELECT id, fecha, total, metodo_pago FROM ventas WHERE id = ?", (id,))
        venta = cursor.fetchone()

        #si el id de la venta no se encontro entonces regresa una mensaje de venta no encontrada
        if not venta:
            conn.close()
            return jsonify({"error": "Venta no encontrada"}), 404

        #si si se econtro el id usamos una consulta para que nos traiga todos los datos de esa venta
        cursor.execute("""
            SELECT m.titulo, d.cantidad, d.precio_unitario, (d.cantidad * d.precio_unitario) as subtotal
            FROM detalle_ventas d
            JOIN mangas m ON d.manga_id = m.id
            WHERE d.venta_id = ?
        """, (id,))
        productos = cursor.fetchall()

        #acomodamos los datos obtenido de la consulta en un diccionario
        respuesta = {
            "id_venta": venta[0],
            "fecha": venta[1],
            "total_pagado": venta[2],
            "metodo_pago": venta[3],
            "articulos": [] #lista donde se guardan todos los articulos de la venta y sus detalles
        }

        #agregamos todos los articulos de la venta en diccionarios en la lista "articulos"
        for p in productos:
            respuesta["articulos"].append({
                "manga": p[0],
                "cantidad": p[1],
                "precio_unitario": p[2],
                "subtotal": p[3]
            })

        conn.close()
        return jsonify(respuesta), 200 #regresamos el diccionario con los valores de la venta
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#POST ventas
@app.route("/ventas", methods=["POST"])
def registrarVenta():
    conn = conexionDB()
    try:
        data = request.json #guardamos los datos que ingreso el usuario en una variable

        #si el usuario no puso ningun producto regresa un mensaje de error
        if "productos" not in data or not data["productos"]:
            return jsonify({"error": "debe incluir al menos un producto"}), 400

        conn = conexionDB()
        cursor = conn.cursor()

        total_venta = 0 #variable con la que calcularemos el total de la venta con los articulos que inserto el usuario
        productos = []

        #ciclo for con el que leeremos cada producto que haya insertado el usuario
        for item in data["productos"]:
            m_id = item["manga_id"]
            cant = item["cantidad"]

            #si la cantidad de mangas es menor a cero se regresa un mensaje de error 
            if cant <= 0:
                return jsonify({"error": f"La cantidad para el manga ID {m_id} debe ser mayor a 0"}), 400
            metodo_pago = data.get("metodo_pago", "Efectivo")
            if metodo_pago not in ["Efectivo", "Tarjeta"]:
                return jsonify({"error": "Método de pago no válido. Debe ser 'Efectivo' o 'Tarjeta'."}), 400
             
            
            
            #con una consulta nos traemos el precio, stock y el titulo del manga que coincida con el id insertado por el usuario
            cursor.execute("SELECT precio, stock, titulo FROM mangas WHERE id = ?", (m_id,))
            manga = cursor.fetchone() #guardamos los resultados de la consulta en una variable

            #si la consulta no nos devolvio algo sale un mensaje de error que ese manga no existe
            if not manga:
                return jsonify({"error": f"Manga con ID {m_id} no existe"}), 404
            
            #acomodamos los resultados de la consulta en variables
            precio, stock, titulo = manga 
            if stock < cant:#si el stock del manga es menor a la que solicita el usuario entonces mandamos un mensade de error
                return jsonify({"error": f"Stock insuficiente para {titulo}"}), 400
            
            total_venta += (precio * cant) #calcualamos y acumulamos el precio de cada manga respecto a la cantidad ingresada

            #guardamos los datos de los mangas en la lista productos
            productos.append({
                "id": m_id,
                "cantidad": cant,
                "precio": precio
            })
            fecha_sistema = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #obtenemos la fecha y hora del sistema para guardarla en la base de datos
         
        #creamos una venta y le asignamos al campo total ell valor de la variable "total_venta"
        cursor.execute("""
            INSERT INTO ventas (fecha, total, metodo_pago) 
            VALUES (?, ?, ?)
        """, (fecha_sistema, total_venta, metodo_pago))
        
        nueva_venta_id = cursor.lastrowid #obtenemos el id que le asigno a nuestra venta la base de datos

        #insertamos los detalles de la venta en la tabla "detalle_ventas"
        for prod in productos:
            cursor.execute("""
                INSERT INTO detalle_ventas (venta_id, manga_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            """, (nueva_venta_id, prod["id"], prod["cantidad"], prod["precio"]))
            
            #actualizamos el stock en la tabla "mangas"
            cursor.execute("UPDATE mangas SET stock = stock - ? WHERE id = ?", (prod["cantidad"], prod["id"]))
    
        conn.commit()
        conn.close()

        #mostramos un mensaje de exito de que se proceso exitosamente la venta junto con el id de la venta y el total pagado 
        return jsonify({
            "mensaje": "venta procesada con exito",
            "venta_id": nueva_venta_id,
            "metodo_pago": metodo_pago,
            "total_pagado": total_venta}), 201
    
    except Exception as e:
        conn.rollback() # Si algo falló en el proceso, deshacemos todo
        conn.close()
        return jsonify({"error": str(e)}), 500
    
#DELETE ventas
@app.route("/ventas/<int:id>", methods=["DELETE"])
def eliminarVenta(id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()

        #seleccionamos el id del manga y la cantidad que coincidan con el id de la venta 
        cursor.execute("SELECT manga_id, cantidad FROM detalle_ventas WHERE venta_id = ?", (id,))
        detalles = cursor.fetchall()  #guardamos los resultados de la consulta en una variable

        #si la consulta no nos dio un resultado entonces mandamos un mensaje de error
        if not detalles:
            conn.close()
            return jsonify({"error": "Venta no encontrada"}), 404

        # actualizamos el stock sumnado la cantidad que obtuvimos de la consulta anterior
        for d in detalles:
            m_id, cant = d
            cursor.execute("UPDATE mangas SET stock = stock + ? WHERE id = ?", (cant, m_id))

        #eliminamos todos lo registros de la tabla "detalle_ventas" donde este el id de la tabla "ventas"
        cursor.execute("DELETE FROM detalle_ventas WHERE venta_id = ?", (id,))
        #eliminamos el registro de la tabla "ventas" que tenga el id ingresado por el usurio 
        cursor.execute("DELETE FROM ventas WHERE id = ?", (id,))

        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Venta eliminada ocancelada y stock restaurado"}), 200 #mensaje de la eliminacion se llevo a cabo exitosamente
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#actualizar ventas
@app.route("/ventas/<int:id>", methods=["PUT"])
def actualizarVenta(id):
    try:
        data = request.json #obtenemos los datos ingresados por el usuario
        
        if "productos" not in data or len(data["productos"]) == 0: #si no se encuntra nada en la consulta del usuario lanza un mensaje de error
            return jsonify({
                "error": "La venta debe tener al menos un producto."
            }), 400
        nuevo_metodo_pago = data.get("metodo_pago")
        conn = conexionDB()
        cursor = conn.cursor()
        
        # Verificar que la venta existe y obtener método actual
        cursor.execute("SELECT metodo_pago FROM ventas WHERE id = ?", (id,))
        venta_actual = cursor.fetchone()
        if not venta_actual:
            conn.close()
            return jsonify({"error": "Venta no encontrada"}), 404
        if nuevo_metodo_pago not in ["Efectivo", "Tarjeta"]:
                return jsonify({"error": "Método de pago no válido. Debe ser 'Efectivo' o 'Tarjeta'."}), 400
        
        # Si no enviaron un nuevo método, nos quedamos con el que ya tenía la base de datos
        if not nuevo_metodo_pago:
            nuevo_metodo_pago = venta_actual[0]

        #seleccionamos el id de la venta que coincida con el id que ingresp el usuario
        cursor.execute("SELECT id FROM ventas WHERE id = ?", (id,))
        if not cursor.fetchone(): #si no hubo resultado lanza un mensaje de error de que no se encontro la venta
            conn.close()
            return jsonify({"error": "Venta no encontrada"}), 404

        #seleccionamos el id del manga junto con la cantidad para restablecer el stock antes de que se realizara la venta
        cursor.execute("SELECT manga_id, cantidad FROM detalle_ventas WHERE venta_id = ?", (id,))
        detalles_anteriores = cursor.fetchall()
        for detalle in detalles_anteriores:
            m_id_viejo, cant_vieja = detalle
            cursor.execute("UPDATE mangas SET stock = stock + ? WHERE id = ?", (cant_vieja, m_id_viejo)) #aqui actualizamos el stock a como estava antes de la venta

        #aqui empezaremos a actualizar la venta con los nuevos valores
        total_nuevo = 0
        productos_para_insertar = []

        #ciclo para validar los nuevos cambios
        for item in data["productos"]:
            m_id = item.get("manga_id")
            cant = item.get("cantidad")

            #si la nueva cantidad es menor a cero o nula lanza un mensaje de error
            if cant is None or cant <= 0:
                conn.rollback() #este rollback es para que regrese la tabla a su estado original antes de actualizar en caso de que la cantidda haya sido menor a cero o nula
                conn.close()
                return jsonify({"error": f"La cantidad para el manga ID {m_id} debe ser mayor a 0"}), 400

            #seleccionamos precio, stock y titulos del manga del id ingresado
            cursor.execute("SELECT precio, stock, titulo FROM mangas WHERE id = ?", (m_id,))
            manga = cursor.fetchone()

            #si no hubo coincidencia en la busqueda lanza mensaje de error y rollback
            if not manga:
                conn.rollback()
                conn.close()
                return jsonify({"error": f"El manga con ID {m_id} no existe"}), 404
            
            precio, stock_actual, titulo = manga
            
            #si el stock es menor a la cantidad solicitada lanza mensaje de error y rollback
            if stock_actual < cant:
                conn.rollback()
                conn.close()
                return jsonify({"error": f"Stock insuficiente para '{titulo}'. Disponible: {stock_actual}"}), 400
            
            total_nuevo += (precio * cant) #calculamos el el nuevo total respecto al precio y la nueva cantidad
            productos_para_insertar.append({
                "id": m_id,
                "cantidad": cant,
                "precio": precio
            })

        cursor.execute("UPDATE ventas SET total = ?, metodo_pago = ? WHERE id = ?", (total_nuevo, nuevo_metodo_pago, id)) #actualizamos la tabla "ventas" con el nuevo total y método de pago
        
        cursor.execute("DELETE FROM detalle_ventas WHERE venta_id = ?", (id,)) #eliminamos los detalles anteriores para reemplazarlos por los nuevos

        for prod in productos_para_insertar:
            #insertamos los nuevos detalles
            cursor.execute("""
                INSERT INTO detalle_ventas (venta_id, manga_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            """, (id, prod["id"], prod["cantidad"], prod["precio"]))
            
            cursor.execute("UPDATE mangas SET stock = stock - ? WHERE id = ?", (prod["cantidad"], prod["id"])) #descontamos el nuevo stock

        conn.commit()
        conn.close()

        #mensaje de actualizacion realizada con exito
        return jsonify({
            "mensaje": "Venta actualizada correctamente",
            "venta_id": id,
            "nuevo_total": total_nuevo,
            "nuevo_metodo_pago": nuevo_metodo_pago
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
 #ENDPOINTS CREADOS PARA FILTRAR INFORMACION PARA LO VISUAL
# Nuevo endpoint para estadísticas del panel

@app.route("/stats/diarias", methods=["GET"])
def obtenerStatsDiarias():
    try:
        # Obtenemos el día actual del sistema local
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        conn = conexionDB()
        cursor = conn.cursor()
        
        # Cantidad total de ventas del día
        cursor.execute("SELECT COUNT(*) FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",))
        total_ventas = cursor.fetchone()[0] or 0

        # Suma de ventas en EFECTIVO hoy
        cursor.execute("""
            SELECT SUM(total) FROM ventas 
            WHERE fecha LIKE ? AND metodo_pago = 'Efectivo'
        """, (f"{hoy}%",))
        efectivo = cursor.fetchone()[0] or 0

        # Suma de ventas con TARJETA hoy
        cursor.execute("""
            SELECT SUM(total) FROM ventas 
            WHERE fecha LIKE ? AND metodo_pago = 'Tarjeta'
        """, (f"{hoy}%",))
        tarjeta = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Devolvemos todo desglosado y el total acumulado (efectivo + tarjeta)
        return jsonify({
            "ventas_dia": total_ventas,
            "efectivo": efectivo,
            "tarjeta": tarjeta,
            "total_acumulado": efectivo + tarjeta
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
 # GET: Obtener la imagen de todos los mangas
@app.route("/mangas/imagenes/todas", methods=["GET"])
def obtenerImagenMangatodas():
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("SELECT id, url_imagen, manga_id FROM manga_imagenes")
        filas = cursor.fetchall()
        conn.close()

        if filas:
            return jsonify({"imagenes": [{"id": fila[0], "url": fila[1], "manga_id": fila[2]} for fila in filas]}), 200
        return jsonify({"mensaje": "No se encontraron imágenes para los mangas"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    # GET: Obtener la imagen de un manga específico
@app.route("/mangas/imagenes/<int:manga_id>", methods=["GET"])
def obtenerImagenManga(manga_id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("SELECT url_imagen FROM manga_imagenes WHERE manga_id = ?", (manga_id,))
        fila = cursor.fetchone()
        conn.close()

        if fila:
            return jsonify({"manga_id": manga_id, "url_imagen": fila[0]}), 200
        return jsonify({"mensaje": "No se encontró imagen para este manga"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST: Asociar una imagen a un manga (puede ser una lista de asociaciones)   
@app.route("/mangas/imagenes", methods=["POST"])
def asociarImagen():
    try:
        datos = request.get_json()
        conn = conexionDB()
        cursor = conn.cursor()
      #si manda una lista de objetos JSON para asociar varias imagenes a varios mangas
        if isinstance(datos, list):
            for item in datos:
                cursor.execute("""
                    INSERT INTO manga_imagenes (manga_id, url_imagen) 
                    VALUES (?, ?)
                """, (item['manga_id'], item['url_imagen']))
        else:
            # Si manda solo un objeto JSON
            cursor.execute("""
                INSERT INTO manga_imagenes (manga_id, url_imagen) 
                VALUES (?, ?)
            """, (datos['manga_id'], datos['url_imagen']))

        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Imagen(es) asociada(s) con éxito"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#  Actualizar la imagen de un manga
@app.route("/mangas/imagenes/<int:manga_id>", methods=["PUT"])
def actualizarImagenManga(manga_id):
    try:
        datos = request.get_json()
        nueva_url = datos.get('url_imagen')
        
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE manga_imagenes 
            SET url_imagen = ? 
            WHERE manga_id = ?
        """, (nueva_url, manga_id))
        
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Imagen actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Eliminar la relación de imagen
@app.route("/mangas/imagenes/img/<manga_id>", methods=["DELETE"])
def eliminarImagenManga(manga_id):
    try:
        conn = conexionDB()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM manga_imagenes WHERE manga_id = ?", (manga_id,))
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Relación de imagen eliminada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    
    
    
if __name__ == "__main__":
    inicializarDB() 
    app.run(debug=True)