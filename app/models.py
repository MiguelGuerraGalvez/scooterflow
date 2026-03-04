from sqlalchemy import Column, String, Integer, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional
from app.database import Base

class Zona(Base):
    # Modelo de la tabla 'zonas' de la base de datos
    __tablename__ = "zonas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    codigo_postal = Column(Integer)
    limite_velocidad = Column(Integer)
    patinetes = relationship("Patinete", back_populates="zona")

class ZonaBase(BaseModel):
    # Modelo base para la creación y actualización de zonas
    nombre: str
    codigo_postal: int
    limite_velocidad: int

class ZonaCreate(ZonaBase):
    # Modelo para la creación de nuevas zonas
    pass

class ZonaUpdate(ZonaBase):
    # Modelo para la actualización de las zonas
    nombre: Optional[str] = None
    codigo_postal: Optional[int] = None
    limite_velocidad: Optional[int] = None

class ZonaResponse(ZonaBase):
    # Modelo para enviar la información de la zona al cliente
    id: int
    class ConfigDict:
        from_attributes = True

class Patinete(Base):
    # Modelo de la tabla 'patinetes' de la base de datos
    __tablename__ = "patinetes"
    id = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(Integer)
    modelo = Column(String)
    bateria = Column(Integer, default=0)
    estado = Column(Enum("disponible", "en_uso", "mantenimiento", "sin_bateria", name="estado"), default="disponible")
    puntuacion_usuario = Column(Float)
    zona_id = Column(Integer, ForeignKey("zonas.id"))
    zona = relationship("Zona", back_populates="patinetes")

class PatineteBase(BaseModel):
    # Modelo base para la creación y actualización de patinetes
    numero_serie: int
    modelo: str
    # Hacemos que la batería sea mínimo 0 y máximo 100
    bateria: int = Field(..., ge=0, le=100, description="La batería tiene que estar entre 0 y 100")
    estado: str
    puntuacion_usuario: float
    zona_id: int

class PatineteCreate(PatineteBase):
    # Modelo para la creación de patinetes
    pass

class PatineteUpdate(PatineteBase):
    # Modelo para la actualización de patinetes
    numero_serie: Optional[int] = None
    modelo: Optional[str] = None
    # Hacemos que la batería sea mínimo 0 y máximo 100
    bateria: Optional[int] = Field(None, ge=0, le=100, description="La batería tiene que estar entre 0 y 100")
    estado: Optional[str] = None
    puntuacion_usuario: Optional[float] = None
    zona_id: Optional[int] = None
