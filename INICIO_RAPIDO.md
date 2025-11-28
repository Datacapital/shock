# 🚀 INICIO RÁPIDO - Dashboard Renta Variable

## Pasos para Poner en Marcha

### 1️⃣ Configurar Supabase (5 minutos)

1. Ve a https://supabase.com y crea una cuenta gratuita
2. Crea un nuevo proyecto
3. Ve a SQL Editor y ejecuta el contenido de `supabase_schema.sql`
4. Copia tu URL del proyecto y la Anon Key (en Project Settings → API)

### 2️⃣ Configurar Variables de Entorno (2 minutos)

1. Copia `.env.example` a `.env`
2. Completa con tus credenciales:
   ```
   SUPABASE_URL=tu-url-aqui
   SUPABASE_KEY=tu-key-aqui
   ```

### 3️⃣ Probar Localmente (Opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Poblar base de datos con datos de ejemplo
python utils.py
# Selecciona opción 1 para poblar acciones de ejemplo

# Iniciar servidor
python main.py
```

Abre http://localhost:8000 en tu navegador

### 4️⃣ Desplegar en Render (10 minutos)

#### A. Preparar Repositorio Git

```bash
git init
git add .
git commit -m "Initial commit"
```

#### B. Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Crea un repositorio nuevo
3. Sigue las instrucciones para subir tu código:

```bash
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git branch -M main
git push -u origin main
```

#### C. Desplegar en Render

1. Ve a https://dashboard.render.com
2. Click en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente la configuración
5. En "Environment Variables", agrega:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - (Opcional) `BINANCE_API_KEY` y `BINANCE_API_SECRET`
   - (Opcional) `BVC_API_URL` y `BVC_API_KEY`
6. Click en "Create Web Service"

¡Listo! En unos minutos tu aplicación estará en línea.

### 5️⃣ Verificar que Todo Funciona

1. Visita tu URL de Render: `https://tu-app.onrender.com`
2. Deberías ver el dashboard
3. Ve a `https://tu-app.onrender.com/docs` para ver la API

### 6️⃣ Poblar Datos Iniciales

Una vez desplegado:

```bash
# Llamar al endpoint de actualización manual
curl -X POST https://tu-app.onrender.com/api/actualizar \
  -H "Content-Type: application/json" \
  -d '{"tarea": "todo"}'
```

O usa el script de utilidades localmente:
```bash
python utils.py
# Selecciona opción 1: Poblar acciones de ejemplo
# Selecciona opción 4: Actualizar precios ahora
```

## ⚙️ Personalización

### Cambiar Hora de Actualización

Por defecto: 5:00 PM (17:00)

Para cambiar, edita en la tabla `configuracion` de Supabase:

```sql
UPDATE configuracion 
SET valor = '18:00'  -- Nueva hora en formato 24h
WHERE clave = 'hora_actualizacion_bvc';
```

### Agregar Más Criptomonedas

Edita `scheduler.py`, línea ~80:
```python
simbolos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT']
```

## 🐛 Solución Rápida de Problemas

### "No se conecta a Supabase"
✅ Verifica que copiaste bien la URL y KEY (sin espacios)

### "No aparecen datos en el dashboard"
✅ Ejecuta actualización manual: `POST /api/actualizar`
✅ Pobla acciones de ejemplo con `utils.py`

### "Render dice 'Application failed to respond'"
✅ Revisa los logs en Render Dashboard
✅ Verifica que todas las variables de entorno estén configuradas

### "Las actualizaciones automáticas no funcionan"
✅ Verifica que el scheduler esté activo: visita `/api/config`
✅ En free tier de Render, el servicio se duerme - las actualizaciones lo despertarán

## 📱 Uso del Dashboard

### Ver Todas las Acciones
- La tabla principal muestra todas las acciones con precios actuales

### Analizar una Acción
- Selecciona una acción del dropdown
- Verás gráfico de evolución de 30 días
- Precios oficial y paralelo
- Capitalización de mercado

### Ver Criptomonedas
- Panel inferior muestra precios actuales de Binance
- Se actualiza cada 5 minutos automáticamente

## 🔄 Mantenimiento

### Actualización Manual
```bash
POST /api/actualizar
Content-Type: application/json
{"tarea": "todo"}
```

### Ver Estado del Sistema
```bash
GET /api/health
```

### Ver Última Actualización
```bash
GET /api/ultima-actualizacion
```

## 📞 ¿Necesitas Ayuda?

1. Revisa los logs en Render Dashboard
2. Consulta el README.md completo
3. Verifica la documentación de la API en `/docs`

---

¡Disfruta tu nuevo dashboard automatizado! 🎉
