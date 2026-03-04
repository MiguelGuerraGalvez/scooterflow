import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Cargamos los datos del archivo .env
load_dotenv()

# Obtenemos la URL de la base de datos
uri = os.getenv("DB_URL")

# SQLAlchemy requiere 'postgresql://' en lugar de 'postgres://'
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

DATABASE_URL = uri

# Configuramos el engine
engine = create_engine(DATABASE_URL)

# Creamos la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    # Creamos la clase Base para los modelos
    pass

def get_db():
    # Creamos la dependencia para inyectar la sesión en los modelos
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
