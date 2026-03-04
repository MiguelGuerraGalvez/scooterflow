from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Zona, ZonaCreate, ZonaUpdate, Patinete, PatineteCreate, PatineteUpdate
from app.database import get_db

app = FastAPI()

@app.get("/")
async def root():
    return {
        "bienvenida": "¡Bienvenid@ a Scooter Flow!",
        "mensaje": "Para poder ver todas las acciones "
        "que puedes realizar, accede a /docs"
    }

@app.get("/zonas")
async def get_zonas(db: Session = Depends(get_db)):
    # Recogemos todos los datos y los mostramos
    return db.query(Zona).all()

@app.post("/zonas/create")
async def post_zonas(zona: ZonaCreate, db: Session = Depends(get_db)):
    # Rellenamos los campos
    db_zona = Zona(
        nombre = zona.nombre,
        codigo_postal = zona.codigo_postal,
        limite_velocidad = zona.limite_velocidad
    )
    db.add(db_zona)
    db.commit()
    db.refresh(db_zona)
    return db_zona

@app.put("/zonas/update/{zona_id}")
async def put_zonas(zona_id: int, zona_update: ZonaUpdate, db: Session = Depends(get_db)):
    # Buscamos al zona en la base de datos
    db_zona = db.query(Zona).filter(Zona.id == zona_id).first()

    if not db_zona:
        # Lanzamos un error si no existe la zona
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    # Excluimos los datos que estén en blanco
    actualizar_datos = zona_update.model_dump(exclude_unset=True)

    for clave, valor in actualizar_datos.items():
        # Actualizamos los cambios
        setattr(db_zona, clave, valor)

    db.commit()
    db.refresh(db_zona)
    return db_zona

@app.delete("/zonas/delete/{zona_id}")
async def delete_zonas(zona_id: int, db: Session = Depends(get_db)):
    # Buscamos a la zona en la base de datos
    db_zona = db.query(Zona).filter(Zona.id == zona_id).first()

    if not db_zona:
        # Lanzamos un error si no existe la zona
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    db.delete(db_zona)
    db.commit()
    return {"detail": "Zona eliminada correctamente"}

@app.post("/zonas/{zona_id}/mantenimiento")
async def post_zonas_mantenimiento(zona_id: int, db: Session = Depends(get_db)):
    db_zona = db.query(Zona).filter(Zona.id == zona_id).first()

    if not db_zona:
        # Lanzamos un error si no existe la zona
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    for patinete in db_zona.patinetes:
        if patinete.bateria < 15:
            patinete.estado = "mantenimiento"

    db.commit()
    db.refresh(db_zona)
    return db_zona.patinetes

@app.get("/patinetes")
async def get_patinetes(patinete_ciudad: Optional[str] = None, db: Session = Depends(get_db)):
    ''' Recogemos todos los patinetes o, si se pasa una ciudad, recogemos los
    patinetes que estén en esa ciudad'''
    query = db.query(Patinete)
    
    if patinete_ciudad:
        # Recogemos los patinetes según la ciudad, si esta se ha enviado
        query = query.join(Patinete.zona).filter(Zona.codigo_postal.ilike(f"%{patinete_ciudad}%"))
    
    return query.all()

@app.post("/patinetes")
async def post_patinetes(patinete: PatineteCreate, db: Session = Depends(get_db)):
    # Rellenamos los campos
    db_patinete = Patinete(
        numero_serie = patinete.numero_serie,
        modelo = patinete.modelo,
        bateria = patinete.bateria,
        estado = patinete.estado,
        puntuacion_usuario = patinete.puntuacion_usuario,
        zona_id = patinete.zona_id
    )
    db.add(db_patinete)
    db.commit()
    db.refresh(db_patinete)
    return db_patinete

'''
@app.patch("/patinetes/{patinete_id}/comprar")
async def patch_patinetes(cantidad: int, patinete_id: int, db: Session = Depends(get_db)):
    # Buscamos al patinete en la base de datos
    db_patinete = db.query(Patinete).filter(Patinete.id == patinete_id).first()

    if not db_patinete:
        # Lanzamos un error si no existe el patinete
        raise HTTPException(status_code=404, detail="Patinete no encontrado")

    if cantidad < 0:
        # Lanzamos un error si la cantidad es negativa
        raise HTTPException(status_code=400, detail="No se pueden vender un número negativo de entradas")
    elif cantidad + db_patinete.tickets_vendidos > db_patinete.zona.capacidad:
        # Lanzamos un error si el total de los tickets vendidos superan la capacidad de la zona
        raise HTTPException(status_code=400, detail="No se pueden vender más entradas que la capacidad disponible")
    else:    
        db_patinete.tickets_vendidos += cantidad
    
    db.commit()
    db.refresh(db_patinete)
    return db_patinete
'''

@app.put("/patinetes/{patinete_id}")
async def put_patinetes(patinete_id: int, patinete_update: PatineteUpdate, db: Session = Depends(get_db)):
    # Buscamos al patinete en la base de datos
    db_patinete = db.query(Patinete).filter(Patinete.id == patinete_id).first()

    if not db_patinete:
        # Lanzamos un error si no existe el patinete
        raise HTTPException(status_code=404, detail="Patinete no encontrado")
    
    # Excluimos los datos que estén en blanco
    actualizar_datos = patinete_update.model_dump(exclude_unset=True)

    for clave, valor in actualizar_datos.items():
        # Actualizamos los datos
        setattr(db_patinete, clave, valor)
    
    db.commit()
    db.refresh(db_patinete)
    return db_patinete

@app.delete("/patinetes/{patinete_id}")
async def delete_patinetes(patinete_id: int, db: Session = Depends(get_db)):

    # Buscamos al patinete en la base de datos
    db_patinete = db.query(Patinete).filter(Patinete.id == patinete_id).first()

    if not db_patinete:
        # Lanzamos un error si no existe el patinete
        raise HTTPException(status_code=404, detail="Patinete no encontrado")
    
    db.delete(db_patinete)
    db.commit()
    return {"detail": "Patinete eliminado correctamente"}
