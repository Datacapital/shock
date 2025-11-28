# 📊 Dashboard Renta Variable 2025 - BVC

Sistema automatizado para monitoreo de acciones de la Bolsa de Valores de Caracas (BVC) con actualización automática diaria.

## ✨ APIs REALES Implementadas

✅ **Bolsa de Valores de Caracas (BVC)** - Scraping directo desde bolsadecaracas.com  
✅ **Banco Central de Venezuela (BCV)** - Tasa oficial mediante scraping  
✅ **Binance P2P** - Tasa paralelo (promedio ponderado top 5 ofertas USDT/VES)  

## 🚀 Características

- ✅ Actualización automática L-V a las 5 PM (17:00) zona América/Caracas
- ✅ Extrae datos de ~30 acciones de la BVC
- ✅ Convierte precios a USD (oficial y paralelo)
- ✅ Calcula capitalizaciones de mercado
- ✅ Dashboard web moderno y responsive
- ✅ Base de datos Supabase
- ✅ Despliegue automático en Render

## 📦 Lo que incluye

- **Backend FastAPI** con todas las APIs reales integradas
- **Scraping BCV** para tasa oficial
- **Binance P2P** para tasa paralelo
- **Scraping BVC** para precios de acciones
- **Frontend moderno** con gráficos interactivos
- **Base de datos Supabase** optimizada
- **Scheduler automático** para actualizaciones diarias

## 🔧 Configuración (3 pasos)

### 1️⃣ Supabase (5 minutos)

```bash
1. Crear cuenta en https://supabase.com
2. Crear nuevo proyecto
3. En SQL Editor, ejecutar el contenido de supabase_schema.sql
4. Copiar URL y Anon Key (Settings → API)
```

### 2️⃣ Variables de Entorno (1 minuto)

Crear archivo `.env`:

```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-aqui
```

¡Eso es todo! No necesitas API keys de BVC ni Binance. Todo funciona con scraping.

### 3️⃣ Desplegar en Render (10 minutos)

```bash
# 1. Subir a GitHub
git init
git add .
git commit -m "Dashboard BVC"
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git push -u origin main

# 2. En Render:
- New Web Service
- Conectar tu repositorio
- Configurar variables de entorno:
  * SUPABASE_URL
  * SUPABASE_KEY
- Deploy!
```

## 🧪 Probar Localmente (Opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Probar APIs
python utils.py
# Opciones:
# 2. Probar BCV (tasa oficial)
# 3. Probar Binance P2P (tasa paralelo)
# 4. Probar BVC (3 acciones de prueba)

# Iniciar servidor
python main.py
# Visita http://localhost:8000
```

## 📊 Cómo Funciona

### Actualización Automática Diaria

**Lunes a Viernes 17:00 (América/Caracas):**

1. **16:50** - Obtiene tasa oficial del BCV (scraping)
2. **16:50** - Obtiene tasa paralelo de Binance P2P (API)
3. **17:00** - Extrae precios de ~30 acciones de BVC (scraping)
4. **17:00** - Convierte todo a USD (oficial y paralelo)
5. **17:00** - Calcula capitalizaciones
6. **17:00** - Guarda en Supabase

### APIs Utilizadas

#### 1. Bolsa de Valores de Caracas (BVC)
```python
# Extrae datos de:
simbolos = ['ABC.A', 'ALZ.B', 'BNC', 'BPV', 'BVCC', 'BVL', 
            'CCR', 'CGQ', 'CRM.A', 'DOM', 'EFE', 'ENV', 
            'FNC', 'GMC.B', 'GZL', 'ICP.B', 'IVC.A', 'IVC.B', 
            'MPA', 'MTC.B', 'MVZ.A', 'MVZ.B', 'PGR', 'PIV.B', 
            'PTN', 'RST', 'RST.B', 'SVS', 'TDV.D']

# Endpoint: https://www.bolsadecaracas.com/wp-admin/admin-ajax.php
# Método: POST scraping
```

#### 2. Banco Central de Venezuela (BCV)
```python
# Scraping de: https://www.bcv.org.ve/estadisticas/tasa-de-cambio
# Extrae: Tasa oficial Bs/USD
# Actualización: Diaria
```

#### 3. Binance P2P
```python
# API: https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search
# Par: USDT/VES
# Cálculo: Promedio ponderado por volumen (top 5 ofertas)
```

## 🌐 Endpoints de la API

```bash
# Salud del sistema
GET /api/health

# Resumen del mercado
GET /api/resumen

# Acciones
GET /api/acciones
POST /api/acciones

# Precios BVC
GET /api/precios/bvc
GET /api/precios/bvc/{codigo}/ultimo
GET /api/precios/bvc/{codigo}/historico?dias=30

# Tasas de cambio
GET /api/tasas
GET /api/tasas/actual  # En tiempo real

# Actualización manual (testing)
POST /api/actualizar
```

## 📁 Estructura del Proyecto

```
├── main.py              # API FastAPI
├── services.py          # APIs BVC, BCV, Binance P2P
├── scheduler.py         # Automatización
├── database.py          # Supabase
├── config.py            # Configuración
├── utils.py             # Utilidades y testing
├── supabase_schema.sql  # Schema DB
├── requirements.txt     # Dependencias
├── Dockerfile          # Docker
├── render.yaml         # Config Render
├── static/
│   └── index.html      # Frontend
└── README.md           # Este archivo
```

## ⚡ Uso del Script de Utilidades

```bash
python utils.py

# Menú:
1. Poblar acciones de BVC
2. Probar BCV (tasa oficial)
3. Probar Binance P2P (tasa paralelo)
4. Probar BVC (3 acciones de prueba)
5. Actualizar precios AHORA (¡tarda ~5 min!)
6. Ver resumen del mercado
7. Verificar configuración
```

## 🔍 Detalles Técnicos

### Ajustes Especiales Implementados

El sistema incluye ajustes específicos para ciertas acciones:

**BNC:**
- Fechas: 2024-12-30, 2025-01-02/03/07/08
- Ajuste: Precio × 1000, Títulos ÷ 1000

**BPV:**
- Fechas antes de: 2025-02-03
- Ajuste: Precio × 0.63423423

### Tasas de Cambio

- **Oficial:** Scraping directo del BCV
- **Paralelo:** Promedio ponderado por volumen de top 5 ofertas P2P
- Actualización: Antes de procesar precios BVC

### Capitalización de Mercado

```
Cap = Precio_USD × Acciones_Circulación
```

Se calcula tanto con dólar oficial como paralelo.

## 🐛 Solución de Problemas

### "Error al obtener tasa BCV"
- El BCV puede estar caído
- Cambió la estructura HTML de su web
- Verificar en `services.py` clase `BCVService`

### "Error Binance P2P"
- Revisar conexión a internet
- Binance puede bloquear IPs en algunos países
- Usar VPN si es necesario

### "No se obtienen datos BVC"
- La BVC puede estar en mantenimiento
- Verificar que sea día laborable
- El scraping tarda ~5 minutos para todas las acciones

### "Error de Supabase"
- Verificar SUPABASE_URL y SUPABASE_KEY
- Confirmar que el schema SQL se ejecutó correctamente
- Revisar límites del plan gratuito

## 📝 Notas Importantes

1. **Scraping Legal:** El scraping de datos públicos de BVC y BCV es legal en Venezuela para uso personal.

2. **Rate Limiting:** El sistema incluye delays (1.5s entre acciones) para no saturar servidores.

3. **Días Laborables:** La actualización automática solo ocurre L-V, siguiendo el calendario bursátil.

4. **Free Tier de Render:**
   - Se duerme después de 15 min de inactividad
   - Las actualizaciones programadas lo despiertan
   - Para 24/7, usar plan pago (~$7/mes)

5. **Precisión de Datos:**
   - Tasa oficial BCV: 100% precisa (fuente oficial)
   - Tasa paralelo: Promedio P2P, puede variar vs. otras fuentes
   - Precios BVC: Directos de la bolsa

## 🔄 Mantenimiento

### Actualizar Hora de Ejecución

```sql
-- En Supabase SQL Editor
UPDATE configuracion 
SET valor = '18:00'  -- Nueva hora
WHERE clave = 'hora_actualizacion_bvc';
```

### Agregar Nueva Acción

```bash
POST /api/acciones
{
  "codigo": "NUEVA",
  "nombre": "Nueva Acción S.A.",
  "acciones_circulacion": 1000000
}
```

Luego agregar el código a `services.py` en la lista `SIMBOLOS`.

## 📊 Dashboard Web

Accede a `https://tu-app.onrender.com` para ver:

- **Resumen general:** Total acciones, capitalizaciones
- **Tasas de cambio:** Oficial (BCV) y Paralelo (P2P) en tiempo real
- **Tabla de acciones:** Todos los precios actualizados
- **Análisis individual:** Gráfico de evolución de 30 días
- **Auto-refresh:** Cada 5 minutos

## 🎯 Próximas Mejoras (Opcional)

- [ ] Alertas por email/Telegram
- [ ] Análisis técnico (RSI, MACD)
- [ ] Comparación con índices internacionales
- [ ] Export a Excel
- [ ] Histórico de más de 30 días

## 📞 Soporte

- Logs en Render: https://dashboard.render.com
- Supabase: https://supabase.com/dashboard
- API Docs: https://tu-app.onrender.com/docs

---

**Creado para PER CAPITAL 2025** 🚀

¡Disfruta tu dashboard automatizado de la BVC!
