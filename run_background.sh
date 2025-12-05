#!/bin/bash

# Script para ejecutar el Dashboard BVC en segundo plano

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Dashboard BVC en segundo plano...${NC}"

# Verificar si ya está corriendo
if [ -f "dashboard.pid" ]; then
    PID=$(cat dashboard.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  El servidor ya está corriendo con PID: $PID${NC}"
        echo -e "${YELLOW}Para detenerlo, ejecuta: ./stop_server.sh${NC}"
        exit 1
    else
        # El PID existe pero el proceso no, limpiar
        rm -f dashboard.pid
    fi
fi

# Verificar que exista el archivo .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: No se encontró archivo .env${NC}"
    echo -e "${YELLOW}Por favor crea el archivo .env con tus credenciales de Supabase${NC}"
    exit 1
fi

# Verificar que las dependencias estén instaladas
if ! pip list | grep -q "fastapi"; then
    echo -e "${YELLOW}⚠️  Instalando dependencias...${NC}"
    pip install -r requirements.txt
fi

# Crear directorio para logs si no existe
mkdir -p logs

# Iniciar servidor en segundo plano
echo -e "${GREEN}📦 Iniciando servidor...${NC}"
nohup python main.py > logs/dashboard.log 2>&1 &

# Guardar PID
echo $! > dashboard.pid

# Esperar un poco para que inicie
sleep 3

# Verificar que esté corriendo
if ps -p $(cat dashboard.pid) > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Servidor iniciado correctamente${NC}"
    echo -e "${GREEN}📊 PID: $(cat dashboard.pid)${NC}"
    echo -e "${GREEN}🌐 URL: http://localhost:8000${NC}"
    echo -e "${GREEN}📄 Logs: tail -f logs/dashboard.log${NC}"
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo -e "  Ver logs en tiempo real: ${GREEN}tail -f logs/dashboard.log${NC}"
    echo -e "  Verificar estado: ${GREEN}./check_status.sh${NC}"
    echo -e "  Detener servidor: ${GREEN}./stop_server.sh${NC}"
else
    echo -e "${RED}❌ Error al iniciar el servidor${NC}"
    echo -e "${YELLOW}Revisa los logs en: logs/dashboard.log${NC}"
    exit 1
fi
