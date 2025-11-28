from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from datetime import date, datetime, timedelta
from database import db
from scheduler import scheduler
from services import binance_p2p_service, bcv_service
from pydantic import BaseModel
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== MODELOS ====================

class AccionCreate(BaseModel):
    codigo: str
    nombre: str
    acciones_circulacion: int

class ActualizarManual(BaseModel):
    tarea: str = "bvc"  # "bvc" o "tasas"


# ==================== APLICACIÓN ====================

app = FastAPI(
    title="Dashboard Renta Variable API",
    description="API para gestión de precios de acciones BVC",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== EVENTOS ====================

@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    logger.info("🚀 Iniciando aplicación...")
    scheduler.start()
    logger.info("✅ Aplicación iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación"""
    logger.info("🛑 Cerrando aplicación...")
    scheduler.shutdown()

# ==================== ENDPOINTS PRINCIPALES ====================

@app.get("/")
async def root():
    """Endpoint raíz - Retorna página HTML del dashboard"""
    try:
        if os.path.exists("static/index.html"):
            with open("static/index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            return {
                "mensaje": "API Dashboard Renta Variable",
                "version": "1.0.0",
                "documentacion": "/docs",
                "estado": "activo"
            }
    except Exception as e:
        logger.error(f"Error al servir página principal: {e}")
        return {"error": str(e)}

@app.get("/api/health")
async def health_check():
    """Verificar estado de la API"""
    return {
        "estado": "activo",
        "timestamp": datetime.now().isoformat(),
        "scheduler_running": scheduler.scheduler.running
    }

# ==================== ACCIONES ====================

@app.get("/api/acciones")
async def get_acciones(activas_solo: bool = True):
    """Obtener lista de acciones"""
    acciones = await db.get_acciones(activas_solo)
    return {
        "total": len(acciones),
        "acciones": acciones
    }

@app.post("/api/acciones")
async def crear_accion(accion: AccionCreate):
    """Crear nueva acción"""
    success = await db.insert_accion(
        codigo=accion.codigo,
        nombre=accion.nombre,
        acciones_circulacion=accion.acciones_circulacion
    )
    
    if success:
        return {"mensaje": "Acción creada exitosamente", "codigo": accion.codigo}
    else:
        raise HTTPException(status_code=400, detail="Error al crear acción")

# ==================== PRECIOS BVC ====================

@app.get("/api/precios/bvc")
async def get_precios_bvc(
    accion: Optional[str] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Obtener precios históricos de BVC"""
    precios = await db.get_precios_bvc(
        accion_codigo=accion,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=limit
    )
    
    return {
        "total": len(precios),
        "precios": precios
    }

@app.get("/api/precios/bvc/{accion_codigo}/ultimo")
async def get_ultimo_precio_bvc(accion_codigo: str):
    """Obtener último precio de una acción"""
    precio = await db.get_ultimo_precio_bvc(accion_codigo)
    
    if not precio:
        raise HTTPException(status_code=404, detail="No se encontró precio para esta acción")
    
    return precio

@app.get("/api/precios/bvc/{accion_codigo}/historico")
async def get_historico_accion(
    accion_codigo: str,
    dias: int = Query(30, ge=1, le=365)
):
    """Obtener histórico de precios de una acción"""
    fecha_inicio = date.today() - timedelta(days=dias)
    
    precios = await db.get_precios_bvc(
        accion_codigo=accion_codigo,
        fecha_inicio=fecha_inicio,
        limit=dias
    )
    
    return {
        "accion": accion_codigo,
        "dias": dias,
        "total_registros": len(precios),
        "precios": precios
    }

# ==================== TASAS DE CAMBIO ====================

@app.get("/api/tasas")
async def get_tasas_cambio(fecha: Optional[date] = None):
    """Obtener tasa de cambio"""
    tasa = await db.get_tasa_cambio(fecha)
    
    if not tasa:
        raise HTTPException(status_code=404, detail="No se encontró tasa de cambio")
    
    return tasa

@app.get("/api/tasas/actual")
async def get_tasa_actual():
    """Obtener tasas actuales en tiempo real (BCV y Binance P2P)"""
    try:
        # Obtener tasa oficial BCV
        tasa_bcv = bcv_service.get_official_rate()
        
        # Obtener tasa paralelo Binance P2P
        tasa_paralelo = binance_p2p_service.get_precio_promedio_compra()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "tasa_oficial": tasa_bcv['tasa_oficial'] if tasa_bcv else None,
            "tasa_paralelo": tasa_paralelo,
            "fuente_oficial": "BCV",
            "fuente_paralelo": "Binance P2P"
        }
    except Exception as e:
        logger.error(f"Error al obtener tasas actuales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RESUMEN Y ESTADÍSTICAS ====================

@app.get("/api/resumen")
async def get_resumen_mercado():
    """Obtener resumen general del mercado"""
    resumen = await db.get_resumen_mercado()
    return resumen

@app.get("/api/resumen/{accion_codigo}")
async def get_resumen_accion(accion_codigo: str):
    """Obtener resumen de una acción específica"""
    precio_actual = await db.get_ultimo_precio_bvc(accion_codigo)
    
    if not precio_actual:
        raise HTTPException(status_code=404, detail="Acción no encontrada")
    
    fecha_inicio = date.today() - timedelta(days=30)
    historico = await db.get_precios_bvc(
        accion_codigo=accion_codigo,
        fecha_inicio=fecha_inicio
    )
    
    if historico:
        precios_oficiales = [float(p['precio_cierre_usd_oficial']) for p in historico if p.get('precio_cierre_usd_oficial')]
        
        if precios_oficiales:
            precio_min = min(precios_oficiales)
            precio_max = max(precios_oficiales)
            precio_promedio = sum(precios_oficiales) / len(precios_oficiales)
        else:
            precio_min = precio_max = precio_promedio = None
    else:
        precio_min = precio_max = precio_promedio = None
    
    return {
        "codigo": accion_codigo,
        "precio_actual_oficial": precio_actual.get('precio_cierre_usd_oficial'),
        "precio_actual_paralelo": precio_actual.get('precio_cierre_usd_paralelo'),
        "capitalizacion_oficial": precio_actual.get('capitalizacion_oficial'),
        "capitalizacion_paralelo": precio_actual.get('capitalizacion_paralelo'),
        "fecha": precio_actual.get('fecha'),
        "estadisticas_30d": {
            "precio_minimo": precio_min,
            "precio_maximo": precio_max,
            "precio_promedio": precio_promedio
        }
    }

# ==================== ACTUALIZACIONES MANUALES ====================

@app.post("/api/actualizar")
async def actualizar_manual(datos: ActualizarManual):
    """Ejecutar actualización manual de precios"""
    try:
        await scheduler.ejecutar_ahora(datos.tarea)
        return {
            "mensaje": f"Actualización '{datos.tarea}' ejecutada exitosamente",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en actualización manual: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ultima-actualizacion")
async def get_ultima_actualizacion():
    """Obtener información de última actualización"""
    ultima_bvc = await db.get_config('ultima_actualizacion_bvc')
    
    return {
        "ultima_actualizacion_bvc": ultima_bvc,
        "proxima_actualizacion": "Lunes a Viernes 17:00 (America/Caracas)"
    }

# ==================== CONFIGURACIÓN ====================

@app.get("/api/config")
async def get_configuracion():
    """Obtener configuración actual del sistema"""
    return {
        "timezone": "America/Caracas",
        "hora_actualizacion_bvc": await db.get_config('hora_actualizacion_bvc'),
        "dias_actualizacion": "Lunes a Viernes",
        "scheduler_activo": scheduler.scheduler.running
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
