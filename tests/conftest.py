import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Creamos una fábrica de sesiones para los tests
DATABASE_URL = os.getenv("DB_URL", "postgresql://user:user@localhost:5432/scooter")
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_db():
    # Crea las tablas antes de los tests
    Base.metadata.create_all(bind=engine)
    yield
    # Borramos los datos de testeo al terminar, para no llenar la base de datos con ellos
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(setup_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback() # Esto hace que cada test empiece de cero
    connection.close()

@pytest.fixture
def cliente(db):
    # Inyectamos la sesión de prueba en la app
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Limpiamos el override para no afectar a los otros tests
    app.dependency_overrides.clear()
