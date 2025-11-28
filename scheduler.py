from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date
from database import db
from services import binance_p2p_service, bcv_service, bvc_service
from config import settings
import logging
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdateScheduler:
    """Programador de actualizaciones automáticas"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.timezone = pytz.timezone(settings.timezone)
        
    async def actualizar_precios_bvc(self):
        """Actualizar precios de la BVC"""
        try:
            logger.info("🔄 Iniciando actualización de precios BVC...")
            
            # 1. Obtener tasa oficial del BCV
            logger.info("📊 Obteniendo tasa oficial BCV...")
            tasa_bcv = bcv_service.get_official_rate()
            if not tasa_bcv:
                logger.error("❌ No se pudo obtener tasa oficial BCV")
                return
            
            tasa_oficial = tasa_bcv['tasa_oficial']
            logger.info(f"✅ Tasa oficial BCV: {tasa_oficial:.2f} Bs/USD")
            
            # 2. Obtener tasa paralelo de Binance P2P
            logger.info("📊 Obteniendo tasa paralelo Binance P2P...")
            tasa_paralelo = binance_p2p_service.get_precio_promedio_compra()
            if not tasa_paralelo:
                logger.error("❌ No se pudo obtener tasa paralelo Binance P2P")
                return
            
            logger.info(f"✅ Tasa paralelo P2P: {tasa_paralelo:.2f} Bs/USD")
            
            # 3. Guardar tasas en la base de datos
            await db.insert_tasa_cambio(
                fecha=date.today(),
                tasa_oficial=tasa_oficial,
                tasa_paralelo=tasa_paralelo
            )
            
            # 4. Obtener precios de cierre de BVC con conversión a USD
            logger.info("📊 Obteniendo precios de cierre BVC...")
            precios = bvc_service.get_precios_cierre(tasa_oficial, tasa_paralelo)
            
            if not precios:
                logger.warning("⚠️  No se obtuvieron precios de la BVC")
                return
            
            # 5. Calcular capitalización con acciones en circulación
            logger.info("💹 Calculando capitalizaciones...")
            acciones = await db.get_acciones()
            acciones_dict = {a['codigo']: a['acciones_circulacion'] for a in acciones}
            
            for precio in precios:
                codigo = precio['accion_codigo']
                if codigo in acciones_dict and acciones_dict[codigo]:
                    acc_circ = acciones_dict[codigo]
                    precio['capitalizacion_oficial'] = precio['precio_cierre_usd_oficial'] * acc_circ
                    precio['capitalizacion_paralelo'] = precio['precio_cierre_usd_paralelo'] * acc_circ
            
            # 6. Insertar precios en la base de datos
            exitos = 0
            errores = 0
            
            for precio in precios:
                success = await db.insert_precio_bvc(precio)
                if success:
                    exitos += 1
                else:
                    errores += 1
            
            logger.info(f"✅ Actualización BVC completada: {exitos} exitosos, {errores} errores")
            
            # 7. Actualizar configuración de última actualización
            await db.update_config('ultima_actualizacion_bvc', datetime.now().isoformat())
            
        except Exception as e:
            logger.error(f"❌ Error en actualización de precios BVC: {e}")
    
    async def actualizar_tasa_cambio(self):
        """Actualizar solo las tasas de cambio (ejecutar antes de actualizar BVC)"""
        try:
            logger.info("🔄 Actualizando tasas de cambio...")
            
            # Obtener tasa oficial BCV
            tasa_bcv = bcv_service.get_official_rate()
            if not tasa_bcv:
                logger.error("❌ No se pudo obtener tasa oficial BCV")
                return
            
            # Obtener tasa paralelo Binance P2P
            tasa_paralelo = binance_p2p_service.get_precio_promedio_compra()
            if not tasa_paralelo:
                logger.error("❌ No se pudo obtener tasa paralelo Binance P2P")
                return
            
            # Guardar tasas
            success = await db.insert_tasa_cambio(
                fecha=date.today(),
                tasa_oficial=tasa_bcv['tasa_oficial'],
                tasa_paralelo=tasa_paralelo
            )
            
            if success:
                logger.info(f"✅ Tasas actualizadas - Oficial: {tasa_bcv['tasa_oficial']:.2f}, Paralelo: {tasa_paralelo:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error al actualizar tasas de cambio: {e}")
    
    def start(self):
        """Iniciar el programador de tareas"""
        try:
            # Obtener hora de actualización desde configuración
            hora, minuto = settings.hora_actualizacion_bvc.split(':')
            
            # Programar actualización de tasas 10 minutos antes
            self.scheduler.add_job(
                self.actualizar_tasa_cambio,
                CronTrigger(hour=int(hora), minute=int(minuto)-10, timezone=self.timezone),
                id='actualizar_tasas',
                name='Actualizar tasas de cambio',
                replace_existing=True
            )
            logger.info(f"📅 Programada actualización de tasas 10 min antes")
            
            # Programar actualización BVC de lunes a viernes a las 5 PM
            self.scheduler.add_job(
                self.actualizar_precios_bvc,
                CronTrigger(
                    day_of_week='mon-fri',  # Solo días laborables
                    hour=int(hora), 
                    minute=int(minuto), 
                    timezone=self.timezone
                ),
                id='actualizar_bvc',
                name='Actualizar precios BVC',
                replace_existing=True
            )
            logger.info(f"📅 Programada actualización BVC L-V a las {settings.hora_actualizacion_bvc}")
            
            # Iniciar el scheduler
            self.scheduler.start()
            logger.info("✅ Scheduler iniciado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error al iniciar scheduler: {e}")
    
    def shutdown(self):
        """Detener el programador"""
        self.scheduler.shutdown()
        logger.info("🛑 Scheduler detenido")
    
    async def ejecutar_ahora(self, tarea: str = "todo"):
        """Ejecutar una tarea de actualización inmediatamente (para testing)"""
        if tarea == "bvc":
            await self.actualizar_precios_bvc()
        elif tarea == "tasas":
            await self.actualizar_tasa_cambio()
        else:
            await self.actualizar_precios_bvc()


# Instancia global del scheduler
scheduler = UpdateScheduler()
