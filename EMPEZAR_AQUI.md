# ⚡ INICIO ULTRA RÁPIDO - 3 PASOS

## 🎯 PASO 1: Supabase (5 min)

1. Ve a https://supabase.com
2. Crea cuenta y nuevo proyecto
3. En SQL Editor → copia y pega TODO el contenido de `supabase_schema.sql`
4. Click en "Run"
5. Ve a Settings → API → Copia:
   - **Project URL** 
   - **Anon public key**

## 🎯 PASO 2: Configurar .env (1 min)

Crea archivo `.env` con:

```
SUPABASE_URL=tu-url-copiada
SUPABASE_KEY=tu-key-copiada
```

## 🎯 PASO 3: GitHub + Render (10 min)

### GitHub:
```bash
git init
git add .
git commit -m "Dashboard BVC"
git remote add origin https://github.com/TU-USUARIO/dashboard-bvc.git
git push -u origin main
```

### Render:
1. https://dashboard.render.com → New → Web Service
2. Conecta tu repo de GitHub
3. Nombre: `dashboard-bvc`
4. En Environment:
   - `SUPABASE_URL` = tu url
   - `SUPABASE_KEY` = tu key
5. Create Web Service

**¡LISTO!** En 5-10 min estará en línea.

---

## 🧪 OPCIONAL: Probar Antes (Local)

```bash
pip install -r requirements.txt
python utils.py
# Opción 2: Probar BCV
# Opción 3: Probar Binance P2P
# Opción 4: Probar BVC (3 acciones)

python main.py
# Ve a http://localhost:8000
```

---

## 📱 Usar tu Dashboard

URL: `https://tu-app.onrender.com`

- **Acciones:** Todas las de la BVC con precios USD
- **Tasas:** Dólar oficial (BCV) y paralelo (P2P)
- **Gráficos:** Evolución de 30 días por acción
- **Auto-update:** L-V a las 5 PM automático

## ⚠️ IMPORTANTE

### Primera vez:
Después de desplegar, poblar con datos:

```bash
# Opción A: Desde utils.py local
python utils.py
# Selecciona: 1. Poblar acciones
# Luego: 5. Actualizar precios (¡tarda 5 min!)

# Opción B: Desde API
curl -X POST https://tu-app.onrender.com/api/actualizar \
  -H "Content-Type: application/json" \
  -d '{"tarea": "bvc"}'
```

### APIs utilizadas:
- **BVC:** Scraping de bolsadecaracas.com (sin API key)
- **BCV:** Scraping de bcv.org.ve (sin API key)  
- **Binance P2P:** API pública (sin API key)

**¡NO necesitas API keys de nada!** Todo funciona con scraping.

---

## 🆘 Problemas?

### Dashboard no muestra datos
```bash
# Ejecutar actualización manual
POST https://tu-app.onrender.com/api/actualizar
```

### Error de Supabase
- Verifica que el SQL se ejecutó completo
- Confirma URL y KEY correctas

### Render no despliega
- Revisa logs en Render Dashboard
- Confirma que el repo tiene todos los archivos

---

## 📚 Más Info

- **README_FINAL.md** → Documentación completa
- **COMANDOS_UTILES.md** → Cheatsheet de comandos
- `https://tu-app.onrender.com/docs` → API docs

**¡Listo en 15 minutos!** 🚀
