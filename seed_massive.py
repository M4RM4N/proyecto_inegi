# seed_massive.py
import sys
import random
import time
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from faker import Faker
from datetime import date
from constants import DB_CONNECTION_STRING

# --- 1. CONFIGURACIÓN ---
DB_URL = DB_CONNECTION_STRING

# Importar todos los modelos
try:
    from modelo import (
        Base, Administrador, Municipio, Localidad, 
        TipoVivienda, ActividadEconomica, Vivienda, Habitante
    )
except ImportError:
    print("Error: No se pudo importar el 'modelo'. Asegúrate de que el script esté en la raíz.")
    sys.exit(1)

# --- 2. PARÁMETROS DE GENERACIÓN ---
fake = Faker('es_MX') # Nombres y direcciones en español (México)

NUM_LOCALIDADES_POR_MUNICIPIO = 10
NUM_VIVIENDAS_POR_LOCALIDAD = 50
MAX_HABITANTES_POR_VIVIENDA = 7
MAX_ACTIVIDADES_POR_VIVIENDA = 3

# --- 3. DATOS DE CATÁLOGO ---
ADMIN_USER = {"usuario": "admin", "contrasena_hash": "admin123"}

TIPOS_VIVIENDA_LIST = [
    "Vivienda de concreto", "Vivienda de adobe(antiguo)", "Vivienda de ladrillo",
    "Vivienda de madera", "Vivienda de cartón", "Casa de piedra",
    "Vivienda prefabricada", "Material Ecológico", "Casa de paja, ramas o caña",
    "Material Adobe Moderno"
]

ACTIVIDADES_LIST = [
    "Comercio al por menor", "Agricultura", "Ganadería", "Servicios Profesionales", 
    "Industria Manufacturera", "Gobierno", "Educación", "Construcción", 
    "Minería", "Transporte", "Servicios de Salud", "Turismo", 
    "Software y TI", "Trabajo Doméstico no remunerado", "Estudiante"
]

MUNICIPIOS_COAHUILA = [
    "Abasolo", "Acuña", "Allende", "Arteaga", "Candela", "Castaños", "Cuatro Ciénegas",
    "Escobedo", "Francisco I. Madero", "Frontera", "General Cepeda", "Guerrero",
    "Hidalgo", "Jiménez", "Juárez", "Lamadrid", "Matamoros", "Monclova", "Morelos",
    "Múzquiz", "Nadadores", "Nava", "Ocampo", "Parras", "Piedras Negras", "Progreso",
    "Ramos Arizpe", "Sabinas", "Sacramento", "Saltillo", "San Buenaventura",
    "San Juan de Sabinas", "San Pedro", "Sierra Mojada", "Torreón", "Viesca",
    "Villa Unión", "Zaragoza"
]

PARENTESCO_LIST = ["Cónyuge", "Hijo(a)", "Nieto(a)", "Padre/Madre", "Suegro(a)", "Yerno/Nuera", "Otro familiar"]
SEXO_LIST = ['F', 'M']

# --- 4. INICIALIZACIÓN DE BBDD ---
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

def seed_data_massive():
    """
    Puebla la base de datos con datos masivos de prueba.
    """
    print("--- INICIANDO POBLADO MASIVO (SEEDING) ---")
    start_time = time.time()
    
    session = SessionLocal()
    
    try:
        # --- 5. VERIFICACIÓN ---
        admin_exists = session.scalar(select(Administrador).where(Administrador.usuario == ADMIN_USER["usuario"]))
        if admin_exists:
            print("Error: La base de datos ya parece estar poblada (el usuario 'admin' existe).")
            print("Por favor, vacía las tablas ('DROP TABLE ...') antes de ejecutar el seeder masivo.")
            return

        # --- 6. POBLAR CATÁLOGOS (Sin dependencias) ---
        print(f"Generando 1 Administrador, {len(TIPOS_VIVIENDA_LIST)} Tipos de Vivienda, {len(ACTIVIDADES_LIST)} Actividades y {len(MUNICIPIOS_COAHUILA)} Municipios...")
        
        # Administrador
        admin = Administrador(usuario=ADMIN_USER["usuario"], contrasena_hash=ADMIN_USER["contrasena_hash"])
        session.add(admin)
        
        # Tipos de Vivienda
        tipos_v_obj = [TipoVivienda(nombre=n) for n in TIPOS_VIVIENDA_LIST]
        session.add_all(tipos_v_obj)
        
        # Actividades Económicas
        act_obj = [ActividadEconomica(nombre=n) for n in ACTIVIDADES_LIST]
        session.add_all(act_obj)
        
        # Municipios
        muni_obj_map = {nombre: Municipio(nombre=nombre) for nombre in MUNICIPIOS_COAHUILA}
        session.add_all(muni_obj_map.values())
        
        # Commit inicial para que los catálogos existan
        session.commit()
        print("-> Catálogos base creados.")

        # --- 7. POBLAR LOCALIDADES (Depende de Municipio) ---
        total_localidades = len(MUNICIPIOS_COAHUILA) * NUM_LOCALIDADES_POR_MUNICIPIO
        print(f"Generando {total_localidades} localidades ({NUM_LOCALIDADES_POR_MUNICIPIO} por municipio)...")
        
        localidades_list = []
        for muni_nombre, muni_obj in muni_obj_map.items():
            for i in range(NUM_LOCALIDADES_POR_MUNICIPIO):
                # Usar nombres de colonias/calles ficticias para las localidades
                loc_nombre = f"{fake.street_name()} (Sección {i+1})"
                loc = Localidad(nombre=loc_nombre, municipio=muni_obj)
                localidades_list.append(loc)
        
        session.add_all(localidades_list)
        session.commit() # Commit para que las localidades existan antes que las viviendas
        print(f"-> {len(localidades_list)} Localidades creadas.")

        # --- 8. POBLAR VIVIENDAS, HABITANTES y ASOCIACIONES M:M ---
        total_viviendas = len(localidades_list) * NUM_VIVIENDAS_POR_LOCALIDAD
        print(f"Generando {total_viviendas} viviendas ({NUM_VIVIENDAS_POR_LOCALIDAD} por localidad)...")
        print("Esto puede tardar varios minutos...")

        viviendas_list = []
        habitantes_list = []
        
        # Listas de objetos ya creados (eficiencia)
        # (Necesitamos recargarlos en la nueva sesión)
        localidades_db = session.scalars(select(Localidad)).all()
        tipos_v_db = session.scalars(select(TipoVivienda)).all()
        actividades_db = session.scalars(select(ActividadEconomica)).all()

        for i, loc in enumerate(localidades_db):
            if (i + 1) % 50 == 0: # Log de progreso
                print(f"  ...Procesando localidad {i+1} de {len(localidades_db)}")
                
            for _ in range(NUM_VIVIENDAS_POR_LOCALIDAD):
                # (A) Crear Vivienda
                total_hab_para_vivienda = random.randint(1, MAX_HABITANTES_POR_VIVIENDA)
                
                vivienda = Vivienda(
                    direccion=fake.address(),
                    fecha_censo=fake.date_between(start_date='-1y', end_date='today'),
                    localidad=loc,
                    tipo_vivienda=random.choice(tipos_v_db),
                    # IMPORTANTE: Convertir a String (VARCHAR) como definiste
                    total_habitantes=str(total_hab_para_vivienda) 
                )
                
                # (B) Crear Asociación M:M (Actividades)
                num_actividades = random.randint(1, MAX_ACTIVIDADES_POR_VIVIENDA)
                actividades_seleccionadas = random.sample(actividades_db, num_actividades)
                vivienda.actividades = actividades_seleccionadas
                
                # (C) Crear Habitantes
                for j in range(total_hab_para_vivienda):
                    sexo = random.choice(SEXO_LIST)
                    nombre = fake.first_name_female() if sexo == 'F' else fake.first_name_male()
                    apellido1 = fake.last_name()
                    apellido2 = fake.last_name()
                    
                    if j == 0:
                        parentesco = "Jefe(a) de Familia"
                    else:
                        parentesco = random.choice(PARENTESCO_LIST)
                    
                    hab = Habitante(
                        nombre_completo=f"{nombre} {apellido1} {apellido2}",
                        edad=random.randint(0, 95), # De 0 a 95 años
                        sexo=sexo,
                        parentesco_con_jefe_familia=parentesco,
                        vivienda=vivienda # SQLAlchemy maneja el FK
                    )
                    habitantes_list.append(hab)
                
                viviendas_list.append(vivienda)
        
        print("Añadiendo viviendas y habitantes a la sesión...")
        session.add_all(viviendas_list)
        session.add_all(habitantes_list)

        # --- 9. COMMIT MASIVO ---
        print("Todos los objetos generados.")
        print("Iniciando COMMIT masivo a la base de datos (esto es lo más tardado)...")
        session.commit()
        
        end_time = time.time()
        print("\n--- ¡POBLADO MASIVO COMPLETO! ---")
        print(f"Tiempo total: {end_time - start_time:.2f} segundos.")
        print(f"Total Viviendas: {len(viviendas_list)}")
        print(f"Total Habitantes: {len(habitantes_list)}")
        
    except Exception as e:
        print("\n--- ERROR DURANTE EL SEEDING ---")
        print(f"Error: {e}")
        print("Revirtiendo la transacción (rollback)...")
        session.rollback()
    finally:
        session.close()

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    print("ADVERTENCIA: Este script poblará masivamente la base de datos definida en DB_URL.")
    print("Asegúrate de que las tablas estén vacías y que la BBDD exista.")
    
    # Asegurar que las tablas existan (main.py también lo hace)
    try:
        print("Verificando/Creando tablas...")
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"No se pudieron crear las tablas (¿Error de conexión?): {e}")
        sys.exit(1)
    
    seed_data_massive()