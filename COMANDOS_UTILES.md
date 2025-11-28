# 📝 COMANDOS ÚTILES - Cheatsheet

## 🚀 Inicio Rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales

# 3. Poblar base de datos
python utils.py
# Selecciona opción 1

# 4. Iniciar servidor
python main.py
```

## 🔧 Comandos de Desarrollo

### Iniciar Servidor Local
```bash
# Modo desarrollo (con recarga automática)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# O simplemente
python main.py
```

### Usar Script de Utilidades
```bash
python utils.py

# Opciones disponibles:
# 1. Poblar acciones de ejemplo
# 2. Probar Binance
# 3. Probar BVC
# 4. Actualizar precios ahora
# 5. Ver resumen del mercado
# 6. Verificar configuración
```

## 🐳 Docker

### Construir Imagen
```bash
docker build -t dashboard-renta-variable .
```

### Ejecutar Contenedor
```bash
docker run -p 8000:8000 \
  -e SUPABASE_URL="tu-url" \
  -e SUPABASE_KEY="tu-key" \
  dashboard-renta-variable
```

### Usar Docker Compose (crear docker-compose.yml)
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

```bash
docker-compose up -d
```

## 📦 Git y GitHub

### Inicializar Repositorio
```bash
git init
git add .
git commit -m "Initial commit: Dashboard Renta Variable"
```

### Conectar a GitHub
```bash
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git branch -M main
git push -u origin main
```

### Actualizar Repositorio
```bash
git add .
git commit -m "Descripción de cambios"
git push
```

## 🌐 API - Comandos cURL

### Health Check
```bash
curl https://tu-app.onrender.com/api/health
```

### Ver Resumen del Mercado
```bash
curl https://tu-app.onrender.com/api/resumen
```

### Ver Acciones
```bash
curl https://tu-app.onrender.com/api/acciones
```

### Actualizar Precios Manualmente
```bash
curl -X POST https://tu-app.onrender.com/api/actualizar \
  -H "Content-Type: application/json" \
  -d '{"tarea": "todo"}'
```

### Ver Último Precio de una Acción
```bash
curl https://tu-app.onrender.com/api/precios/bvc/BBVA/ultimo
```

### Ver Histórico de Acción (30 días)
```bash
curl https://tu-app.onrender.com/api/precios/bvc/BBVA/historico?dias=30
```

### Ver Precio Actual de Bitcoin
```bash
curl https://tu-app.onrender.com/api/precios/binance/BTCUSDT/actual
```

### Crear Nueva Acción
```bash
curl -X POST https://tu-app.onrender.com/api/acciones \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "NUEVA",
    "nombre": "Nueva Acción S.A.",
    "acciones_circulacion": 1000000
  }'
```

## 🗄️ Supabase - SQL útil

### Ver todas las acciones
```sql
SELECT * FROM acciones ORDER BY codigo;
```

### Ver últimos precios
```sql
SELECT * FROM precios_bvc 
ORDER BY fecha DESC 
LIMIT 10;
```

### Ver resumen de una acción
```sql
SELECT * FROM get_resumen_accion('BBVA');
```

### Cambiar hora de actualización
```sql
UPDATE configuracion 
SET valor = '18:00' 
WHERE clave = 'hora_actualizacion_bvc';
```

### Ver última actualización
```sql
SELECT * FROM configuracion 
WHERE clave LIKE '%ultima_actualizacion%';
```

### Borrar todos los precios (CUIDADO!)
```sql
-- Solo usar en desarrollo/testing
DELETE FROM precios_bvc;
DELETE FROM precios_binance;
```

## 🔍 Debugging

### Ver Logs en Render
1. Ve a Render Dashboard
2. Selecciona tu servicio
3. Click en "Logs"
4. Filtra por errores

### Ver Logs Localmente
```bash
# Los logs se imprimen en la consola
python main.py

# Para guardar logs en archivo:
python main.py > app.log 2>&1
```

### Probar Conexión a Supabase
```python
python -c "
from database import db
import asyncio
async def test():
    acciones = await db.get_acciones()
    print(f'Acciones encontradas: {len(acciones)}')
asyncio.run(test())
"
```

### Probar Binance
```python
python -c "
from services import binance_service
import asyncio
async def test():
    precio = await binance_service.get_precio_actual('BTCUSDT')
    print(f'Precio BTC: ${precio:,.2f}')
asyncio.run(test())
"
```

## 📊 Monitoreo

### Verificar si el Scheduler está Activo
```bash
curl https://tu-app.onrender.com/api/config
```

### Ver Última Actualización
```bash
curl https://tu-app.onrender.com/api/ultima-actualizacion
```

### Forzar Actualización (Testing)
```bash
# Actualizar todo
curl -X POST https://tu-app.onrender.com/api/actualizar \
  -H "Content-Type: application/json" \
  -d '{"tarea": "todo"}'

# Solo BVC
curl -X POST https://tu-app.onrender.com/api/actualizar \
  -H "Content-Type: application/json" \
  -d '{"tarea": "bvc"}'

# Solo Binance
curl -X POST https://tu-app.onrender.com/api/actualizar \
  -H "Content-Type: application/json" \
  -d '{"tarea": "binance"}'
```

## 🛠️ Mantenimiento

### Backup de Base de Datos (Supabase)
1. Ve a Supabase Dashboard
2. Settings → Database
3. Click en "Backup now"

### Restaurar Backup
1. Ve a Supabase Dashboard
2. Settings → Database
3. Selecciona el backup
4. Click en "Restore"

### Actualizar Dependencias
```bash
pip list --outdated
pip install --upgrade nombre-paquete
pip freeze > requirements.txt
```

## 📝 Notas Importantes

### Variables de Entorno Críticas
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...
```

### URLs Importantes
- Dashboard: `https://tu-app.onrender.com`
- API Docs: `https://tu-app.onrender.com/docs`
- Health: `https://tu-app.onrender.com/api/health`
- Logs Render: `https://dashboard.render.com/`
- Supabase: `https://supabase.com/dashboard`

## 🆘 Solución Rápida de Problemas

### Error: "No module named 'X'"
```bash
pip install -r requirements.txt
```

### Error: "Connection to Supabase failed"
```bash
# Verificar credenciales en .env
# Verificar que Supabase esté activo
```

### Error: "Port 8000 already in use"
```bash
# Cambiar puerto
python main.py --port 8001

# O encontrar y matar proceso
lsof -ti:8000 | xargs kill -9
```

### Frontend no carga
```bash
# Verificar que existe static/index.html
ls -la static/
```

---

💡 **Tip**: Guarda este archivo como referencia rápida!
