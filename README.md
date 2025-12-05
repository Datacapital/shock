# 📊 Dashboard Renta Variable 2025 - PER CAPITAL

Sistema automatizado para monitoreo de acciones de la Bolsa de Valores de Caracas (BVC) y criptomonedas de Binance, con actualización automática diaria.

## 🚀 Características

- ✅ Actualización automática de precios BVC a las 5 PM diariamente
- ✅ Actualización automática de precios Binance a las 5 PM diariamente
- ✅ Base de datos Supabase para almacenamiento persistente
- ✅ API REST completa con FastAPI
- ✅ Frontend web moderno y responsive
- ✅ Dashboard en tiempo real con gráficos interactivos
- ✅ Sin sistema de valoraciones (simplificado)
- ✅ Despliegue automático en Render

## 📋 Requisitos Previos

1. Cuenta en [Supabase](https://supabase.com) (gratuita)
2. Cuenta en [Render](https://render.com) (gratuita)
3. APIs de tu bolsa de valores
4. Cuenta Binance (opcional, para más funcionalidades)

## 🛠️ Configuración

### 1. Configurar Supabase

1. Crear nuevo proyecto en Supabase
2. En el SQL Editor, ejecutar el archivo `supabase_schema.sql`
3. Copiar la URL y la Anon Key del proyecto

### 2. Configurar Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```bash
# Supabase (OBLIGATORIO)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anon-key

# Binance (Opcional - para más datos)
BINANCE_API_KEY=tu-api-key
BINANCE_API_SECRET=tu-api-secret

# API BVC (Adaptar según tu API)
BVC_API_URL=https://api-bvc.com
BVC_API_KEY=tu-api-key

# Configuración
TIMEZONE=America/Caracas
```

### 3. Instalar Dependencias Localmente (Desarrollo)

```bash
pip install -r requirements.txt
```

### 4. Ejecutar Localmente

```bash
python main.py
```

La aplicación estará disponible en: `http://localhost:8000`

## 🌐 Despliegue en Render

### Opción 1: Despliegue Automático (Recomendado)

1. **Subir código a GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/tu-usuario/tu-repo.git
   git push -u origin main
   ```

2. **Conectar a Render:**
   - Ve a [Render Dashboard](https://dashboard.render.com)
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub
   - Render detectará automáticamente el `render.yaml`

3. **Configurar Variables de Entorno:**
   - En el dashboard de Render, ve a "Environment"
   - Agrega todas las variables del archivo `.env`

4. **Desplegar:**
   - Click en "Create Web Service"
   - Render construirá y desplegará automáticamente

### Opción 2: Despliegue Manual

1. En Render Dashboard, crear nuevo "Web Service"
2. Seleccionar "Deploy from Docker"
3. Configurar:
   - **Environment**: Docker
   - **Docker Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Port**: 8000

## 📊 Uso de la API

### Endpoints Principales

#### Obtener resumen del mercado
```bash
GET /api/resumen
```

#### Obtener acciones
```bash
GET /api/acciones
```

#### Obtener precios BVC de una acción
```bash
GET /api/precios/bvc/{codigo}/historico?dias=30
```

#### Obtener precio actual de Binance
```bash
GET /api/precios/binance/BTCUSDT/actual
```

#### Actualizar manualmente (para testing)
```bash
POST /api/actualizar
Content-Type: application/json

{
  "tarea": "todo"  # "bvc", "binance", "tasas", o "todo"
}
```

### Documentación Interactiva

Una vez desplegado, visita:
- Swagger UI: `https://tu-app.onrender.com/docs`
- ReDoc: `https://tu-app.onrender.com/redoc`

## 📁 Estructura del Proyecto

```
.
├── main.py                 # Aplicación FastAPI principal
├── database.py            # Operaciones con Supabase
├── services.py            # Servicios para APIs externas
├── scheduler.py           # Automatización de actualizaciones
├── config.py              # Configuración
├── supabase_schema.sql    # Schema de base de datos
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Configuración Docker
├── render.yaml           # Configuración Render
├── .env.example          # Ejemplo de variables de entorno
├── static/
│   └── index.html        # Frontend web
└── README.md             # Este archivo
```

## ⏰ Automatización

El sistema ejecuta automáticamente:

- **4:50 PM**: Actualización de tasas de cambio
- **5:00 PM**: Actualización de precios BVC
- **5:00 PM**: Actualización de precios Binance

Las actualizaciones se ejecutan en zona horaria `America/Caracas` (configurable).

## 🔧 Personalización

### Cambiar hora de actualización

Editar en Supabase (tabla `configuracion`):
```sql
UPDATE configuracion 
SET valor = '18:00' 
WHERE clave = 'hora_actualizacion_bvc';
```

### Agregar nuevas acciones

```bash
POST /api/acciones
Content-Type: application/json

{
  "codigo": "ACCION",
  "nombre": "Nombre de la Acción",
  "acciones_circulacion": 1000000
}
```

### Agregar más criptomonedas

Editar en `scheduler.py`, línea con `simbolos`:
```python
simbolos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'NUEVACRIPTO']
```

## 🐛 Solución de Problemas

### Error de conexión a Supabase
- Verificar que las variables `SUPABASE_URL` y `SUPABASE_KEY` sean correctas
- Confirmar que el schema SQL se ejecutó correctamente

### No se actualizan los precios
- Verificar logs en Render
- Confirmar que las APIs de BVC/Binance funcionan
- Probar actualización manual: `POST /api/actualizar`

### Error en despliegue de Render
- Verificar que todas las variables de entorno estén configuradas
- Revisar logs de build en Render
- Confirmar que el puerto 8000 esté configurado

## 📝 Notas Importantes

1. **API de BVC**: El código incluye implementaciones de ejemplo. Debes adaptarlas a tu API real de la Bolsa de Valores.

2. **Binance**: Si no tienes API keys, el sistema funciona en modo público con limitaciones.

3. **Tasas de Cambio**: Implementar conexión a fuente real (BCV, MonitorDólar, etc.)

4. **Free Tier de Render**: 
   - El servicio gratuito se duerme después de 15 minutos de inactividad
   - Las actualizaciones programadas lo despertarán automáticamente
   - Considera upgrade a plan pago para 24/7 sin interrupciones

## 🔒 Seguridad

- Nunca commits tus archivos `.env` al repositorio
- Usa las variables de entorno de Render para información sensible
- Las API keys deben tener permisos mínimos necesarios

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs en Render Dashboard
2. Consultar documentación de Supabase
3. Verificar estado de las APIs externas

## 📄 Licencia

Este proyecto es de uso interno. Todos los derechos reservados.

---


