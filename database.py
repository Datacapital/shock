from supabase import create_client, Client
from config import settings
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Clase para manejar operaciones con Supabase"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # ==================== ACCIONES ====================
    
    async def get_acciones(self, activas_solo: bool = True) -> List[Dict]:
        """Obtener lista de acciones"""
        try:
            query = self.client.table('acciones').select('*')
            if activas_solo:
                query = query.eq('activa', True)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Error al obtener acciones: {e}")
            return []
    
    async def insert_accion(self, codigo: str, nombre: str, acciones_circulacion: int) -> bool:
        """Insertar nueva acción"""
        try:
            data = {
                'codigo': codigo,
                'nombre': nombre,
                'acciones_circulacion': acciones_circulacion
            }
            self.client.table('acciones').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error al insertar acción {codigo}: {e}")
            return False
    
    # ==================== PRECIOS BVC ====================
    
    async def insert_precio_bvc(self, data: Dict[str, Any]) -> bool:
        """Insertar precio de BVC"""
        try:
            self.client.table('precios_bvc').insert(data).execute()
            logger.info(f"Precio BVC insertado: {data['accion_codigo']} - {data['fecha']}")
            return True
        except Exception as e:
            logger.error(f"Error al insertar precio BVC: {e}")
            return False
    
    async def get_precios_bvc(
        self,
        accion_codigo: Optional[str] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Obtener precios históricos de BVC"""
        try:
            query = self.client.table('precios_bvc').select('*')
            
            if accion_codigo:
                query = query.eq('accion_codigo', accion_codigo)
            if fecha_inicio:
                query = query.gte('fecha', fecha_inicio.isoformat())
            if fecha_fin:
                query = query.lte('fecha', fecha_fin.isoformat())
            
            response = query.order('fecha', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error al obtener precios BVC: {e}")
            return []
    
    async def get_ultimo_precio_bvc(self, accion_codigo: str) -> Optional[Dict]:
        """Obtener el último precio registrado de una acción"""
        try:
            response = self.client.table('precios_bvc')\
                .select('*')\
                .eq('accion_codigo', accion_codigo)\
                .order('fecha', desc=True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error al obtener último precio BVC: {e}")
            return None
    
    # ==================== TASAS DE CAMBIO ====================
    
    async def insert_tasa_cambio(self, fecha: date, tasa_oficial: float, tasa_paralelo: float) -> bool:
        """Insertar tasa de cambio"""
        try:
            data = {
                'fecha': fecha.isoformat(),
                'tasa_oficial': tasa_oficial,
                'tasa_paralelo': tasa_paralelo
            }
            self.client.table('tasas_cambio').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error al insertar tasa de cambio: {e}")
            return False
    
    async def get_tasa_cambio(self, fecha: Optional[date] = None) -> Optional[Dict]:
        """Obtener tasa de cambio de una fecha específica o la más reciente"""
        try:
            query = self.client.table('tasas_cambio').select('*')
            
            if fecha:
                query = query.eq('fecha', fecha.isoformat())
            else:
                query = query.order('fecha', desc=True).limit(1)
            
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error al obtener tasa de cambio: {e}")
            return None
    
    # ==================== RESUMEN Y ESTADÍSTICAS ====================
    
    async def get_resumen_mercado(self) -> Dict[str, Any]:
        """Obtener resumen general del mercado"""
        try:
            # Obtener todas las acciones activas
            acciones = await self.get_acciones()
            
            resumen = {
                'total_acciones': len(acciones),
                'fecha_actualizacion': None,
                'capitalizacion_total_oficial': 0,
                'capitalizacion_total_paralelo': 0,
                'acciones_detalle': []
            }
            
            for accion in acciones:
                ultimo_precio = await self.get_ultimo_precio_bvc(accion['codigo'])
                if ultimo_precio:
                    resumen['acciones_detalle'].append({
                        'codigo': accion['codigo'],
                        'nombre': accion['nombre'],
                        'precio_oficial': ultimo_precio.get('precio_cierre_usd_oficial'),
                        'precio_paralelo': ultimo_precio.get('precio_cierre_usd_paralelo'),
                        'capitalizacion_oficial': ultimo_precio.get('capitalizacion_oficial'),
                        'capitalizacion_paralelo': ultimo_precio.get('capitalizacion_paralelo'),
                        'fecha': ultimo_precio.get('fecha')
                    })
                    
                    if ultimo_precio.get('capitalizacion_oficial'):
                        resumen['capitalizacion_total_oficial'] += float(ultimo_precio['capitalizacion_oficial'])
                    if ultimo_precio.get('capitalizacion_paralelo'):
                        resumen['capitalizacion_total_paralelo'] += float(ultimo_precio['capitalizacion_paralelo'])
                    
                    if not resumen['fecha_actualizacion'] or ultimo_precio['fecha'] > resumen['fecha_actualizacion']:
                        resumen['fecha_actualizacion'] = ultimo_precio['fecha']
            
            return resumen
        except Exception as e:
            logger.error(f"Error al obtener resumen del mercado: {e}")
            return {}
    
    # ==================== CONFIGURACIÓN ====================
    
    async def get_config(self, clave: str) -> Optional[str]:
        """Obtener valor de configuración"""
        try:
            response = self.client.table('configuracion')\
                .select('valor')\
                .eq('clave', clave)\
                .execute()
            
            return response.data[0]['valor'] if response.data else None
        except Exception as e:
            logger.error(f"Error al obtener configuración {clave}: {e}")
            return None
    
    async def update_config(self, clave: str, valor: str) -> bool:
        """Actualizar valor de configuración"""
        try:
            self.client.table('configuracion')\
                .update({'valor': valor, 'updated_at': datetime.now().isoformat()})\
                .eq('clave', clave)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error al actualizar configuración {clave}: {e}")
            return False


# Instancia global de la base de datos
db = Database()
