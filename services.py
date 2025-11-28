import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, date
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceP2PService:
    """Servicio para obtener precio paralelo del dólar desde Binance P2P"""
    
    FRIENDLY_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "Accept-Language": "es-VE,es;q=0.9,en;q=0.8",
        "Origin": "https://p2p.binance.com",
        "Referer": "https://p2p.binance.com/es"
    }
    
    def get_top5_usdt_ves(self) -> List[Dict]:
        """Obtener top 5 ofertas USDT/VES en Binance P2P"""
        try:
            payload = {
                "asset": "USDT",
                "fiat": "VES",
                "tradeType": "BUY",
                "page": 1,
                "rows": 20,
                "payTypes": [],
                "publisherType": None,
                "merchantCheck": False
            }
            
            with requests.Session() as s:
                s.trust_env = False
                s.headers.update(self.HEADERS)
                r = s.post(self.FRIENDLY_URL, json=payload, timeout=15)
                r.raise_for_status()
                j = r.json()
                
                data = (j.get("data") or [])[:5]
                out = []
                
                for it in data:
                    adv = it.get("adv", {}) or {}
                    advr = it.get("advertiser", {}) or {}
                    price = adv.get("price")
                    vol = adv.get("surplusAmount") or adv.get("tradableQuantity")
                    
                    out.append({
                        "price": float(price) if price else None,
                        "volume_usdt": float(vol) if vol else None,
                        "minVES": float(adv.get("minSingleTransAmount")) if adv.get("minSingleTransAmount") else None,
                        "maxVES": float(adv.get("maxSingleTransAmount")) if adv.get("maxSingleTransAmount") else None,
                        "merchant": advr.get("nickName") or advr.get("userNo"),
                        "payments": [m.get("tradeMethodName") for m in (adv.get("tradeMethods") or []) if m.get("tradeMethodName")],
                        "source": {"endpoint": "friendly", "tradeType": "BUY"}
                    })
                
                return out
                
        except Exception as e:
            logger.error(f"Error al obtener precio Binance P2P: {e}")
            return []
    
    def get_precio_promedio_compra(self) -> Optional[float]:
        """Calcular precio promedio de compra ponderado por volumen"""
        try:
            ofertas = self.get_top5_usdt_ves()
            if not ofertas:
                return None
            
            # Calcular promedio ponderado por volumen
            total_volumen = sum(o['volume_usdt'] for o in ofertas if o['volume_usdt'])
            if total_volumen == 0:
                # Si no hay volumen, usar promedio simple
                precios = [o['price'] for o in ofertas if o['price']]
                return sum(precios) / len(precios) if precios else None
            
            precio_ponderado = sum(
                o['price'] * o['volume_usdt'] 
                for o in ofertas 
                if o['price'] and o['volume_usdt']
            ) / total_volumen
            
            logger.info(f"Precio promedio P2P calculado: {precio_ponderado:.2f} VES/USDT")
            return precio_ponderado
            
        except Exception as e:
            logger.error(f"Error al calcular precio promedio P2P: {e}")
            return None


class BCVService:
    """Servicio para obtener tasa oficial del BCV mediante scraping"""
    
    BCV_URL = "https://www.bcv.org.ve/estadisticas/tasa-de-cambio"
    
    def get_official_rate(self) -> Optional[Dict]:
        """Obtener tasa oficial del BCV"""
        try:
            logger.info(f"Iniciando scraping de Tasa Oficial BCV: {self.BCV_URL}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.BCV_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            data_table_wrapper = soup.find('div', class_='view-content')
            
            if not data_table_wrapper:
                logger.error("No se encontró el contenedor de datos del BCV")
                return None
            
            table = data_table_wrapper.find('table')
            if not table:
                logger.error("No se encontró la tabla de datos del BCV")
                return None
            
            first_data_row = table.find('tbody').find('tr')
            if not first_data_row:
                logger.error("No se encontró fila de datos en tabla BCV")
                return None
            
            cells = first_data_row.find_all('td')
            if len(cells) < 2:
                logger.error("Fila sin suficientes celdas en tabla BCV")
                return None
            
            # Extraer fecha y tasa
            fecha_str_raw = cells[0].get_text(strip=True)
            tasa_str_raw = cells[1].get_text(strip=True)
            
            # Procesar fecha
            fecha_obj = None
            for fmt in ('%d-%m-%Y', '%Y-%m-%d'):
                try:
                    fecha_obj = datetime.strptime(fecha_str_raw, fmt).date()
                    break
                except ValueError:
                    continue
            
            if not fecha_obj:
                logger.warning(f"Formato de fecha no reconocido: {fecha_str_raw}")
                fecha_obj = date.today()
            
            # Limpiar tasa (eliminar puntos de miles, cambiar coma por punto)
            tasa_clean = tasa_str_raw.replace('.', '').replace(',', '.')
            tasa_float = float(tasa_clean)
            
            logger.info(f"Tasa oficial BCV obtenida: {tasa_float:.2f} Bs/USD (fecha: {fecha_obj})")
            
            return {
                'fecha': fecha_obj,
                'tasa_oficial': tasa_float
            }
            
        except Exception as e:
            logger.error(f"Error al obtener tasa BCV: {e}")
            return None


class BVCService:
    """Servicio para extraer datos de la Bolsa de Valores de Caracas"""
    
    SIMBOLOS = ['ABC.A', 'ALZ.B', 'BNC', 'BPV', 'BVCC', 'BVL', 'CCR', 'CGQ',
                'CRM.A', 'DOM', 'EFE', 'ENV', 'FNC', 'GMC.B', 'GZL', 'ICP.B',
                'IVC.A', 'IVC.B', 'MPA', 'MTC.B', 'MVZ.A', 'MVZ.B', 'PGR', 
                'PIV.B', 'PTN', 'RST', 'RST.B', 'SVS', 'TDV.D']
    
    def obtener_datos_desnudos(self, simbolo: str) -> Optional[Dict]:
        """Extraer datos desde la API de la BVC"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.bolsadecaracas.com/historicos/"
            }
            
            data = {
                "action": "getHistoricoSimbolo",
                "simbolo": simbolo
            }
            
            response = requests.post(
                "https://www.bolsadecaracas.com/wp-admin/admin-ajax.php",
                headers=headers,
                data=data,
                timeout=15
            )
            
            if response.status_code != 200:
                logger.error(f"Error en respuesta BVC para {simbolo}: {response.status_code}")
                return None
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error procesando {simbolo}: {e}")
            return None
    
    def limpiar_numero(self, valor: str) -> float:
        """Limpiar y convertir strings a números"""
        if pd.isna(valor) or valor == "":
            return np.nan
        
        valor_str = str(valor)
        valor_limpio = valor_str.replace(".", "").replace(",", ".")
        
        try:
            return float(valor_limpio)
        except ValueError:
            return np.nan
    
    def procesar_datos_accion(self, simbolo: str, datos: Dict) -> pd.DataFrame:
        """Procesar datos de una acción específica"""
        if 'cur_hist_mov_emisora' not in datos or datos['cur_hist_mov_emisora'] is None:
            return pd.DataFrame({'ACCION': [simbolo]})
        
        df_data = datos['cur_hist_mov_emisora']
        
        if isinstance(df_data, list):
            df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame([df_data])
        
        if df.empty:
            return pd.DataFrame({'ACCION': [simbolo]})
        
        # Renombrar columnas
        columnas_esperadas = ["FECHA", "PRECIO_APERT", "PRECIO_CIE", "VAR_ABS", "VAR_REL", 
                             "PRECIO_MAX", "PRECIO_MIN", "N_OPERACIONES", 
                             "TITULOS_NEGOCIADOS", "MONTO_EFECTIVO"]
        
        df.columns = columnas_esperadas[:len(df.columns)]
        
        # Convertir fecha
        if 'FECHA' in df.columns:
            df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d-%m-%y', errors='coerce')
        
        # Limpiar columnas numéricas
        columnas_numericas = ['PRECIO_APERT', 'PRECIO_CIE', 'VAR_ABS', 'VAR_REL', 
                             'PRECIO_MAX', 'PRECIO_MIN', 'N_OPERACIONES', 
                             'TITULOS_NEGOCIADOS', 'MONTO_EFECTIVO']
        
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = df[col].apply(self.limpiar_numero)
        
        df['ACCION'] = simbolo
        return df
    
    def get_precios_cierre(self, tasa_oficial: float, tasa_paralelo: float) -> List[Dict]:
        """Obtener todos los precios de cierre del día con conversión a USD"""
        try:
            logger.info("Iniciando extracción de datos BVC...")
            
            # Recoger datos de todas las acciones
            datos_finales = {}
            for simbolo in self.SIMBOLOS:
                logger.info(f"Procesando: {simbolo}")
                datos = self.obtener_datos_desnudos(simbolo)
                if datos is not None:
                    datos_finales[simbolo] = datos
                    time.sleep(1.5)
            
            # Procesar todos los datos
            dataframes = []
            for simbolo, datos in datos_finales.items():
                df = self.procesar_datos_accion(simbolo, datos)
                if not df.empty:
                    dataframes.append(df)
            
            if not dataframes:
                logger.warning("No se obtuvieron datos de BVC")
                return []
            
            datos_totales = pd.concat(dataframes, ignore_index=True)
            
            # Filtrar solo datos del día actual o más reciente
            fecha_hoy = date.today()
            datos_totales['FECHA'] = pd.to_datetime(datos_totales['FECHA'])
            
            # Obtener la fecha más reciente disponible
            fecha_mas_reciente = datos_totales['FECHA'].max()
            datos_dia = datos_totales[datos_totales['FECHA'] == fecha_mas_reciente].copy()
            
            logger.info(f"Datos obtenidos para fecha: {fecha_mas_reciente.date()}")
            
            # Aplicar ajustes específicos para BNC y BPV
            self.aplicar_ajustes(datos_dia)
            
            # Agregar tasas de cambio
            datos_dia['Oficial'] = tasa_oficial
            datos_dia['Paralelo'] = tasa_paralelo
            
            # Crear estructura BVC_USD
            precios = []
            for _, row in datos_dia.iterrows():
                precio_dict = {
                    'accion_codigo': row['ACCION'],
                    'fecha': row['FECHA'].date(),
                    'precio_cierre_bs': row['PRECIO_CIE'],
                    'precio_cierre_usd_oficial': row['PRECIO_CIE'] / tasa_oficial,
                    'precio_cierre_usd_paralelo': row['PRECIO_CIE'] / tasa_paralelo,
                    'monto_efectivo_usd_oficial': row['MONTO_EFECTIVO'] / tasa_oficial,
                    'monto_efectivo_usd_paralelo': row['MONTO_EFECTIVO'] / tasa_paralelo,
                    'num_operaciones': int(row['N_OPERACIONES']) if not pd.isna(row['N_OPERACIONES']) else 0,
                    'titulos_negociados': int(row['TITULOS_NEGOCIADOS']) if not pd.isna(row['TITULOS_NEGOCIADOS']) else 0,
                    'capitalizacion_oficial': None,  # Calcular después con acciones en circulación
                    'capitalizacion_paralelo': None
                }
                precios.append(precio_dict)
            
            logger.info(f"Procesados {len(precios)} registros de BVC")
            return precios
            
        except Exception as e:
            logger.error(f"Error al obtener precios BVC: {e}")
            return []
    
    def aplicar_ajustes(self, datos: pd.DataFrame):
        """Aplicar ajustes específicos para BNC y BPV"""
        # Ajustes BNC
        fechas_bnc = ["2024-12-30", "2025-01-02", "2025-01-03", "2025-01-07", "2025-01-08"]
        fechas_bnc_dt = pd.to_datetime(fechas_bnc)
        
        mask_bnc = (datos['ACCION'] == 'BNC') & (datos['FECHA'].isin(fechas_bnc_dt))
        datos.loc[mask_bnc, 'PRECIO_APERT'] *= 1000
        datos.loc[mask_bnc, 'PRECIO_CIE'] *= 1000
        datos.loc[mask_bnc, 'TITULOS_NEGOCIADOS'] /= 1000
        
        # Ajustes BPV
        fecha_ajuste_bpv = pd.to_datetime("2025-02-03")
        factor_ajuste = 0.63423423
        
        mask_bpv = (datos['ACCION'] == "BPV") & (datos['FECHA'] < fecha_ajuste_bpv)
        datos.loc[mask_bpv, 'PRECIO_CIE'] *= factor_ajuste


# Instancias globales
binance_p2p_service = BinanceP2PService()
bcv_service = BCVService()
bvc_service = BVCService()
