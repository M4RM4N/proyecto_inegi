import sys
from PyQt5.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from constants import DB_CONNECTION_STRING, ASSISTANT_CONNECTION_STRING

# --- 1. IMPORTAR MODELOS (Para creación de tablas) ---
try:
    from modelo import Base
except ImportError as e:
    print(f"Error: No se pudo importar el Modelo. Verifica 'modelo/__init__.py'. {e}")
    sys.exit(1)

# --- 2. IMPORTAR CONTROLADORES ---
try:
    from controlador.AdminController import AdminController
    from controlador.CatalogoController import CatalogoController
    from controlador.CensoController import CensoController
    from controlador.AsistenteController import AsistenteController
except ImportError as e:
    print(f"Error: No se pudieron importar los Controladores. Verifica 'controlador/__init__.py'. {e}")
    sys.exit(1)

# --- 3. IMPORTAR VISTAS ---
try:
    from vista.login_view import LoginView
except ImportError as e:
    print(f"Error: No se pudo importar LoginView. Verifica 'vista/login_view.py'. {e}")
    sys.exit(1)


# --- 4. CONFIGURACIÓN DE BASE DE DATOS ---
# (Asegúrate de que la base de datos que aparece en la url exista en tu MySQL)
DB_URL = DB_CONNECTION_STRING
ASISTENTE_URL = ASSISTANT_CONNECTION_STRING


def inicializar_aplicacion():
    """
    Inicializa la BD, los controladores y la aplicación MVC.
    """
    
    # --- 5. CREAR ENGINE DE SQLALCHEMY ---
    try:
        engine = create_engine(DB_URL)
        asistente_engine = create_engine(ASISTENTE_URL)
        # Intentar una conexión simple para verificar
        with engine.connect() as connection:
            pass
        print("Conexión a MySQL (Engine) exitosa.")
    except OperationalError as e:
        print(f"Error Crítico: No se pudo conectar a la base de datos MySQL.")
        print(f"Detalle: {e}")
        print("Verifica tus credenciales en DB_URL, que el servidor MySQL esté corriendo y que la BD 'inegi (o cualquier nombre que le hayas puesto)' exista.")
        return # No se puede continuar sin BD
    except Exception as e:
        print(f"Error al crear el engine de SQLAlchemy: {e}")
        return

    # --- 6. CREAR TABLAS (Si no existen) ---
    try:
        Base.metadata.create_all(engine)
        print("Tablas del Modelo verificadas/creadas exitosamente.")
    except Exception as e:
        print(f"Error al intentar crear las tablas: {e}")
        return

    # --- 7. INICIALIZAR LA APLICACIÓN PYQT5 ---
    app = QApplication(sys.argv)
    
    # --- 8. INICIALIZAR CONTROLADORES (Inyección de Dependencias) ---
    # Se pasa el 'engine' a los controladores para que sus DAOs puedan usarlo.
    admin_controller = AdminController(engine)
    catalogo_controller = CatalogoController(engine)
    censo_controller = CensoController(engine)
    asistente_controller = AsistenteController(asistente_engine)
    print("Controladores inicializados.")
    
    # --- 9. INICIALIZAR VISTA PRINCIPAL ---
    # Se pasan los controladores a la Vista para que pueda interactuar con ellos.
    login_view = LoginView(
        admin_controller=admin_controller,
        catalogo_controller=catalogo_controller,
        censo_controller=censo_controller,
        asistente_controller=asistente_controller
    )
    
    # --- 10. MOSTRAR Y EJECUTAR ---
    print("Iniciando la aplicación...")
    login_view.show()
    sys.exit(app.exec_())

# --- PUNTO DE ENTRADA DEL PROGRAMA ---
if __name__ == "__main__":
    inicializar_aplicacion()