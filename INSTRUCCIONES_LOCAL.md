# 🚀 Guía de Ejecución Local en Segundo Plano

## 📋 Resumen Rápido

He creado scripts automatizados para ejecutar el Dashboard BVC localmente en segundo plano.

### Scripts Disponibles:

| Script | Descripción |
|--------|-------------|
| `./run_background.sh` | Inicia el servidor en segundo plano |
| `./stop_server.sh` | Detiene el servidor |
| `./check_status.sh` | Verifica el estado completo del servidor |
| `./test_api.sh` | Prueba todos los endpoints de la API |

---

## 🔧 Configuración Inicial (Solo una vez)

### 1. Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales reales de Supabase:

```bash
nano .env
```

Reemplaza estos valores:
```env
SUPABASE_URL=https://tu-proyecto-real.supabase.co
SUPABASE_KEY=tu-clave-anon-key-real-aqui
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecutar en Segundo Plano

### Iniciar el Servidor

```bash
./run_background.sh
```

**Salida esperada:**
```
🚀 Iniciando Dashboard BVC en segundo plano...
📦 Iniciando servidor...
✅ Servidor iniciado correctamente
📊 PID: 12345
🌐 URL: http://localhost:8000
📄 Logs: tail -f logs/dashboard.log
```

### Verificar Estado

```bash
./check_status.sh
```

Esto mostrará:
- ✅ Estado del proceso (corriendo o detenido)
- 🔌 Estado del puerto 8000
- 🌐 Respuesta de la API
- 📄 Últimas líneas del log
- 📚 Lista de endpoints disponibles

### Ver Logs en Tiempo Real

```bash
tail -f logs/dashboard.log
```

Presiona `Ctrl+C` para salir de los logs.

### Probar la API

```bash
./test_api.sh
```

Esto probará todos los endpoints principales y te mostrará si funcionan correctamente.

### Detener el Servidor

```bash
./stop_server.sh
```

---

## 🌐 Acceder al Dashboard

Una vez que el servidor esté corriendo, abre tu navegador en:

- **Dashboard Principal:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

## 🧪 Probar Endpoints Manualmente

### 1. Verificar salud de la API

```bash
curl http://localhost:8000/api/health
```

### 2. Obtener lista de acciones

```bash
curl http://localhost:8000/api/acciones
```

### 3. Obtener tasas de cambio actuales

```bash
curl http://localhost:8000/api/tasas/actual
```

### 4. Obtener resumen del mercado

```bash
curl http://localhost:8000/api/resumen
```

### 5. Actualizar datos manualmente

```bash
curl -X POST http://localhost:8000/api/actualizar \
  -H "Content-Type: application/json" \
  -d '{"tarea": "todo"}'
```

---

## 📊 Estructura de Archivos Creados

```
shock/
├── .env                    # Variables de entorno (configura tus credenciales aquí)
├── run_background.sh       # Script para iniciar servidor
├── stop_server.sh          # Script para detener servidor
├── check_status.sh         # Script para verificar estado
├── test_api.sh            # Script para probar API
├── dashboard.pid          # PID del proceso (se crea automáticamente)
└── logs/
    └── dashboard.log      # Archivo de logs (se crea automáticamente)
```

---

## ⚠️ Solución de Problemas

### El servidor no inicia

1. Verifica que configuraste correctamente el `.env`:
   ```bash
   cat .env
   ```

2. Verifica los logs:
   ```bash
   tail -f logs/dashboard.log
   ```

3. Asegúrate de que el puerto 8000 no esté ocupado:
   ```bash
   netstat -tuln | grep 8000
   # o
   ss -tuln | grep 8000
   ```

### Error de conexión a Supabase

Si ves errores de conexión en los logs:

1. Verifica que tu `SUPABASE_URL` y `SUPABASE_KEY` sean correctas
2. Asegúrate de que el schema SQL esté ejecutado en Supabase
3. Verifica que tengas conexión a internet

### El servidor se detuvo inesperadamente

1. Revisa los logs para ver el error:
   ```bash
   tail -50 logs/dashboard.log
   ```

2. Limpia el archivo PID obsoleto:
   ```bash
   rm -f dashboard.pid
   ```

3. Intenta iniciarlo nuevamente:
   ```bash
   ./run_background.sh
   ```

### Puerto 8000 ocupado

Si el puerto ya está en uso por otro proceso:

```bash
# Encontrar el proceso que usa el puerto
lsof -i :8000

# Matar el proceso
kill -9 <PID>
```

---

## 🔄 Actualización Automática

El sistema está configurado para actualizar automáticamente:

- **4:50 PM**: Tasas de cambio (BCV y Binance P2P)
- **5:00 PM**: Precios de acciones BVC

Estas actualizaciones se ejecutan de lunes a viernes en zona horaria `America/Caracas`.

---

## 💡 Comandos Útiles

### Ver proceso del servidor
```bash
ps aux | grep "python main.py"
```

### Ver uso de recursos
```bash
ps -p $(cat dashboard.pid) -o %cpu,%mem,etime,command
```

### Reiniciar servidor
```bash
./stop_server.sh && ./run_background.sh
```

### Limpiar logs antiguos
```bash
rm logs/dashboard.log
```

---

## 📝 Notas Importantes

1. **Credenciales:** Nunca compartas tu archivo `.env` con tus credenciales reales
2. **Supabase:** Asegúrate de tener el schema SQL ejecutado en tu proyecto
3. **APIs:** Configura las APIs de BVC según tu proveedor
4. **Logs:** Los logs se guardan en `logs/dashboard.log` y crecen con el tiempo

---

## ✅ Checklist de Verificación

- [ ] Archivo `.env` configurado con credenciales reales
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Schema SQL ejecutado en Supabase
- [ ] Servidor iniciado con `./run_background.sh`
- [ ] Estado verificado con `./check_status.sh`
- [ ] API probada con `./test_api.sh` o accediendo a http://localhost:8000/docs
- [ ] Dashboard accesible en http://localhost:8000

---

## 🆘 Necesitas Ayuda?

1. Revisa los logs: `tail -f logs/dashboard.log`
2. Verifica el estado: `./check_status.sh`
3. Prueba los endpoints: `./test_api.sh`
4. Revisa la documentación interactiva: http://localhost:8000/docs
