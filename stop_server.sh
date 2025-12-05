#!/bin/bash

# Script para detener el Dashboard BVC

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Deteniendo Dashboard BVC...${NC}"

# Verificar si existe el archivo PID
if [ ! -f "dashboard.pid" ]; then
    echo -e "${RED}❌ No se encontró dashboard.pid${NC}"
    echo -e "${YELLOW}El servidor podría no estar corriendo${NC}"
    exit 1
fi

# Leer PID
PID=$(cat dashboard.pid)

# Verificar si el proceso está corriendo
if ps -p $PID > /dev/null 2>&1; then
    # Matar el proceso
    kill $PID
    sleep 2

    # Verificar si se detuvo
    if ps -p $PID > /dev/null 2>&1; then
        # Si aún está corriendo, forzar
        echo -e "${YELLOW}Forzando detención...${NC}"
        kill -9 $PID
    fi

    echo -e "${GREEN}✅ Servidor detenido correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  El proceso con PID $PID no está corriendo${NC}"
fi

# Limpiar archivo PID
rm -f dashboard.pid

echo -e "${GREEN}🧹 Limpieza completada${NC}"
