# seed.py
import sys
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from datetime import date
from constants import DB_CONNECTION_STRING

# --- 1. CONFIGURACIÓN ---
# Asegúrate de que esta URL sea la misma que en tu main.py
DB_URL = DB_CONNECTION_STRING

# Importar todos los modelos
try:
    from modelo import (
        Base, Administrador, Municipio, Localidad, 
        TipoVivienda, ActividadEconomica, Vivienda, Habitante
    )
except ImportError:
    print("Error: Asegúrate de que 'modelo' sea un paquete importable.")
    sys.exit(1)

# --- 2. INICIALIZACIÓN ---
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def seed_data():
    """
    Puebla la base de datos con datos de prueba si está vacía.
    """
    print("Iniciando el proceso de poblado (seeding)...")
    
    try:
        # --- 3. VERIFICACIÓN (Para evitar duplicados si se corre de nuevo) ---
        admin_exists = session.scalar(select(Administrador).where(Administrador.usuario == 'admin'))
        if admin_exists:
            print("La base de datos ya parece estar poblada. Abortando.")
            return

        # --- 4. CREACIÓN DE CATÁLOGOS (Sin dependencias) ---
        
        # Administrador
        # (En un proyecto real, esta contraseña debe estar hasheada)
        admin = Administrador(usuario='admin', contrasena_hash='admin123')
        
        # Tipos de Vivienda (Fuente: Documento de requisitos)
        tipos_vivienda_nombres = [
            "Vivienda de concreto", "Vivienda de adobe(antiguo)", "Vivienda de ladrillo",
            "Vivienda de madera", "Vivienda de cartón", "Casa de piedra",
            "Vivienda prefabricada", "Material Ecológico", "Casa de paja, ramas o caña",
            "Material Adobe Moderno"
        ]
        tipos_vivienda_obj = {nombre: TipoVivienda(nombre=nombre) for nombre in tipos_vivienda_nombres}

        # Actividades Económicas
        actividades_nombres = ["Comercio", "Agricultura", "Servicios Profesionales", "Industria", "Gobierno"]
        actividades_obj = {nombre: ActividadEconomica(nombre=nombre) for nombre in actividades_nombres}

        session.add(admin)
        session.add_all(tipos_vivienda_obj.values())
        session.add_all(actividades_obj.values())
        print("-> Administradores y Catálogos creados.")

        # --- 5. UBICACIONES (Con dependencias) ---
        
        # Municipios
        muni_saltillo = Municipio(nombre='Saltillo')
        muni_arteaga = Municipio(nombre='Arteaga')
        muni_torreon = Municipio(nombre='Torreón')
        
        # Localidades (Dependen de Municipio)
        loc_centro_sal = Localidad(nombre='Zona Centro (Saltillo)', municipio=muni_saltillo)
        loc_san_antonio = Localidad(nombre='San Antonio de las Alazanas', municipio=muni_arteaga)
        loc_centro_tor = Localidad(nombre='Centro (Torreón)', municipio=muni_torreon)
        
        session.add_all([muni_saltillo, muni_arteaga, muni_torreon])
        session.add_all([loc_centro_sal, loc_san_antonio, loc_centro_tor])
        print("-> Municipios y Localidades creados.")

        # --- 6. CENSO (Viviendas y Habitantes) ---

        # Vivienda 1 (Saltillo)
        vivienda1 = Vivienda(
            direccion='Calle Ficticia 123',
            fecha_censo=date(2025, 10, 25),
            localidad=loc_centro_sal,
            tipo_vivienda=tipos_vivienda_obj["Vivienda de ladrillo"],
            # Relación M:M (Sostén de la vivienda)
            actividades=[actividades_obj["Comercio"], actividades_obj["Servicios Profesionales"]]
        )
        
        # Vivienda 2 (Arteaga)
        vivienda2 = Vivienda(
            direccion='Camino Real 456',
            fecha_censo=date(2025, 10, 24),
            localidad=loc_san_antonio,
            tipo_vivienda=tipos_vivienda_obj["Vivienda de adobe(antiguo)"],
            actividades=[actividades_obj["Agricultura"]]
        )
        
        session.add_all([vivienda1, vivienda2])
        print("-> Viviendas creadas.")

        # Habitantes (Dependen de Vivienda)
        hab1 = Habitante(nombre_completo='Juan Pérez', edad=45, sexo='M', parentesco_con_jefe_familia='Jefe(a) de Familia', vivienda=vivienda1)
        hab2 = Habitante(nombre_completo='Maria López', edad=42, sexo='F', parentesco_con_jefe_familia='Cónyuge', vivienda=vivienda1)
        hab3 = Habitante(nombre_completo='Luis Pérez', edad=18, sexo='M', parentesco_con_jefe_familia='Hijo(a)', vivienda=vivienda1)
        
        hab4 = Habitante(nombre_completo='Ana García', edad=65, sexo='F', parentesco_con_jefe_familia='Jefe(a) de Familia', vivienda=vivienda2)
        
        session.add_all([hab1, hab2, hab3, hab4])

        # Actualizar contadores (Simulando la lógica del CensoController)
        vivienda1.total_habitantes = 3
        vivienda2.total_habitantes = 1
        
        print("-> Habitantes creados.")

        # --- 7. COMMIT ---
        session.commit()
        print("\n¡Base de datos poblada exitosamente!")
        
    except Exception as e:
        session.rollback()
        print(f"\nError al poblar la base de datos: {e}")
        print("Se ha revertido la transacción (rollback).")
    finally:
        session.close()

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    print("ADVERTENCIA: Este script poblará la base de datos definida en DB_URL.")
    # (Opcional) Crear tablas primero (aunque main.py lo hace)
    # print("Asegurando que las tablas existan...")
    # Base.metadata.create_all(engine)
    
    seed_data()