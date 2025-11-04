import sqlalchemy
from google import genai
from sqlalchemy.exc import SQLAlchemyError
from constants import GEMINI_API_KEY

SCHEMA_DB = """
-- La tabla 'actividad_economica' contiene el catálogo de sostenes económicos.
CREATE TABLE actividad_economica (
        id INTEGER NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (nombre)
);
CREATE TABLE administrador (
        id INTEGER NOT NULL AUTO_INCREMENT,
        usuario VARCHAR(50) NOT NULL,
        contrasena_hash VARCHAR(256) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (usuario)
);

-- Catálogo de municipios. Ejemplo: 'Saltillo', 'Arteaga'.
CREATE TABLE municipio (
        id INTEGER NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (nombre)
);

-- Catálogo de tipos de vivienda. Ejemplo: 'Vivienda de concreto', 'Vivienda de ladrillo'.
CREATE TABLE tipo_vivienda (
        id INTEGER NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(50) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (nombre)
);
CREATE TABLE localidad (
        id INTEGER NOT NULL AUTO_INCREMENT,
        nombre VARCHAR(100) NOT NULL,
        municipio_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(municipio_id) REFERENCES municipio (id)
);
CREATE TABLE vivienda (
        id INTEGER NOT NULL AUTO_INCREMENT,
        direccion VARCHAR(255) NOT NULL,
        fecha_censo DATE,
        coordenadas_gps VARCHAR(50),
        total_habitantes VARCHAR(50),
        localidad_id INTEGER NOT NULL,
        tipo_vivienda_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(localidad_id) REFERENCES localidad (id),
        FOREIGN KEY(tipo_vivienda_id) REFERENCES tipo_vivienda (id)
);

-- Tabla de asociación para vivienda y actividad_economica (Muchos a Muchos)
CREATE TABLE vivienda_actividad (
        vivienda_id INTEGER NOT NULL,
        actividad_id INTEGER NOT NULL,
        PRIMARY KEY (vivienda_id, actividad_id),
        FOREIGN KEY(vivienda_id) REFERENCES vivienda (id),
        FOREIGN KEY(actividad_id) REFERENCES actividad_economica (id)
);

-- Tabla principal de habitantes.
CREATE TABLE habitante (
        id INTEGER NOT NULL AUTO_INCREMENT,
        nombre_completo VARCHAR(150) NOT NULL,
        edad INTEGER NOT NULL,

        -- Columna 'sexo' usa codificación: 'F' = Femenino (Mujer), 'M' = Masculino (Hombre).
        sexo VARCHAR(10) NOT NULL,

        -- Columna 'parentesco' usa valores como: 'Jefe(a) de Familia', 'Cónyuge', 'Hijo(a)'.
        parentesco_con_jefe_familia VARCHAR(50) NOT NULL,
        vivienda_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(vivienda_id) REFERENCES vivienda (id)
);
"""

class AsistenteController:
    """
    Controlador para el asistente de IA
    """

    def __init__(self, engine):
        # Recibe el engine en el main.py, el engine utilizara un usuario que solo tenga privilegios de select
        self.engine = engine

        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model_sql = 'gemini-2.5-flash'
            self.model_chat = 'gemini-2.5-flash'
            print("AsistenteController: Cliente de Gemini inicializado")
        except Exception as e:
            print(f"Error al inicializar el cliente de Gemini: {e}")
            self.client = None

    def chatear(self, pregunta_usuario: str) -> str:
        """
        Toma una pregunta, genera SQL, lo ejecuta y devuelve una respuesta amigable.
        """
        if not self.client:
            return "Error: El cliente de IA no esta inicializado"
        
#         prompt_sql=f"""
# Eres un asistente experto en SQL. Tu tarea es generar una consulta SQL
# basada en el esquema de la base de datos y la pregunta del usuario.

# ### ESQUEMA DE LA BASE DE DATOS ###
# {SCHEMA_DB}

# ### EJEMPLOS (Pregunta -> SQL) ###
# Pregunta: ¿Cuántos habitantes hay en total?
# SQL: SELECT COUNT(*) FROM habitante;

# Pregunta: ¿Cuántas mujeres viven en Saltillo?
# SQL: SELECT COUNT(t1.id) FROM habitante AS t1 JOIN vivienda AS t2 ON t1.vivienda_id = t2.id JOIN localidad AS t3 ON t2.localidad_id = t3.id JOIN municipio AS t4 ON t3.municipio_id = t4.id WHERE t1.sexo = 'F' AND t4.nombre = 'Saltillo';

# Pregunta: ¿Qué actividades económicas sostienen la vivienda de 'Juan Pérez'?
# SQL: SELECT t3.nombre FROM vivienda AS t1 JOIN vivienda_actividad AS t2 ON t1.id = t2.vivienda_id JOIN actividad_economica AS t3 ON t2.actividad_id = t3.id JOIN habitante AS t4 ON t1.id = t4.vivienda_id WHERE t4.nombre_completo = 'Juan Pérez';

# ### REGLAS ###
# - Solo genera la consulta SQL.
# - No incluyas explicaciones, comentarios, markdown (```sql) ni texto adicional.
# - **Solo genera consultas de tipo SELECT.** NUNCA uses DROP, DELETE, UPDATE, INSERT.
# - Si la pregunta no se puede responder con el esquema, responde "ERROR: Imposible de responder".

# ### PREGUNTA DEL USUARIO ###
# {pregunta_usuario}

# ### CONSULTA SQL GENERADA ###
#         """
        prompt_sql=f"""
Eres un asistente experto en SQL. Tu tarea es generar una consulta SQL
basada en el esquema de la base de datos y la pregunta del usuario.

### ESQUEMA DE LA BASE DE DATOS ###
{SCHEMA_DB}

### REGLAS DE GENERACIÓN DE SQL ###
- Solo genera la consulta SQL.
- No incluyas explicaciones, comentarios, markdown (```sql) ni texto adicional.
- **Solo genera consultas de tipo SELECT.** NUNCA uses DROP, DELETE, UPDATE, INSERT.
- Si la pregunta no se puede responder con el esquema, responde "ERROR: Imposible de responder".

### REGLAS DE LÓGICA DE NEGOCIO (¡MUY IMPORTANTE!) ###
1.  **Codificación de Sexo:** La columna 'sexo' usa 'F' para mujeres y 'M' para hombres.
2.  **Conversión de Números (CAST):** La columna 'vivienda.total_habitantes' es un VARCHAR. Para CUALQUIER operación matemática (SUM, AVG, COUNT), DEBES convertirla usando `CAST(total_habitantes AS UNSIGNED)`.
3.  **Búsqueda de Texto:** Las búsquedas de nombres (municipios, personas, etc.) deben ser insensibles a mayúsculas usando `LOWER()` o `UPPER()`.

### EJEMPLOS (Pregunta -> SQL) ###
Pregunta: ¿Cuántos habitantes hay en total?
SQL: SELECT COUNT(*) FROM habitante;

Pregunta: ¿Cuántas mujeres hay?
SQL: SELECT COUNT(*) FROM habitante WHERE sexo = 'F';

Pregunta: ¿Cuántos hombres viven en Saltillo?
SQL: SELECT COUNT(t1.id) FROM habitante AS t1 JOIN vivienda AS t2 ON t1.vivienda_id = t2.id JOIN localidad AS t3 ON t2.localidad_id = t3.id JOIN municipio AS t4 ON t3.municipio_id = t4.id WHERE t1.sexo = 'M' AND LOWER(t4.nombre) = 'saltillo';

Pregunta: ¿Cuál es el total de habitantes censados (usando la columna total_habitantes de vivienda)?
SQL: SELECT SUM(CAST(total_habitantes AS UNSIGNED)) FROM vivienda;

Pregunta: ¿Cuál es el promedio de edad de las mujeres en Torreón?
SQL: SELECT AVG(t1.edad) FROM habitante AS t1 JOIN vivienda AS t2 ON t1.vivienda_id = t2.id JOIN localidad AS t3 ON t2.localidad_id = t3.id JOIN municipio AS t4 ON t3.municipio_id = t4.id WHERE t1.sexo = 'F' AND LOWER(t4.nombre) = 'torreón';

Pregáunta: ¿Cuántas viviendas de 'Vivienda de ladrillo' hay?
SQL: SELECT COUNT(t1.id) FROM vivienda AS t1 JOIN tipo_vivienda AS t2 ON t1.tipo_vivienda_id = t2.id WHERE LOWER(t2.nombre) = 'vivienda de ladrillo';

Pregunta: ¿Qué actividades económicas sostienen la vivienda de 'Ana García'?
SQL: SELECT t3.nombre FROM vivienda AS t1 JOIN vivienda_actividad AS t2 ON t1.id = t2.vivienda_id JOIN actividad_economica AS t3 ON t2.actividad_id = t3.id JOIN habitante AS t4 ON t1.id = t4.vivienda_id WHERE LOWER(t4.nombre_completo) = 'ana garcía';

### PREGUNTA DEL USUARIO ###
{pregunta_usuario}

### CONSULTA SQL GENERADA ###
        """

        try:
            print("[Debug IA] Enviando prompt para generar SQL...")
            respuestas_gemini_sql = self.client.models.generate_content(
                model=self.model_sql,
                contents=prompt_sql
            )
            consulta_sql_generada = respuestas_gemini_sql.text.strip().replace("```sql", "").replace("```", "")

            if not consulta_sql_generada.upper().startswith("SELECT"):
                print(f"[ERROR IA] Consulta no valida: {consulta_sql_generada}")
                return "Lo siento, solo puedo procesar consultas de informacion (SELECT)"
            
            print(f"[Debug IA] SQL Generado: {consulta_sql_generada}")

            with self.engine.connect() as connection:
                resultado = connection.execute(sqlalchemy.text(consulta_sql_generada))
                filas_resultado = resultado.fetchall()

            print(f"[Debu IA] Resultado BD: {filas_resultado}")
            
            prompt_amigable = f"""
Eres un asistente de chat amigable y servicial.
La pregunta original del usuario fue: "{pregunta_usuario}"
Se ejecutó una consulta en la base de datos y el resultado fue: {filas_resultado}

Por favor, responde la pregunta original del usuario en lenguaje natural,
basándote en esos resultados. Sé breve y directo.
Si el resultado está vacío o es '[]', di que no se encontraron datos.
"""
            print("[Debug IA] Enviando Prompt para respuesta amigable...")

            respuesta_gemini_amigable = self.client.models.generate_content(
                model=self.model_chat,
                contents=prompt_amigable
            )

            return respuesta_gemini_amigable.text
        
        except Exception as e:
            print(f"[Error IA] Ha ocurrido un error: {e}")
            return "Lo siento, tuve un problema al procesar tu solicitud"