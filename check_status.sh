#!/bin/bash

# Script para verificar el estado del Dashboard BVC

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📊 Estado del Dashboard BVC${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# 1. Verificar archivo PID
if [ -f "dashboard.pid" ]; then
    PID=$(cat dashboard.pid)
    echo -e "${GREEN}📌 PID encontrado: $PID${NC}"

    # Verificar si el proceso está corriendo
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Servidor está CORRIENDO${NC}"

        # Mostrar información del proceso
        echo -e "\n${BLUE}Información del proceso:${NC}"
        ps aux | grep $PID | grep -v grep

        # Verificar memoria y CPU
        echo -e "\n${BLUE}Uso de recursos:${NC}"
        ps -p $PID -o %cpu,%mem,etime,command | tail -n 1

    else
        echo -e "${RED}❌ El servidor NO está corriendo (PID obsoleto)${NC}"
        echo -e "${YELLOW}Limpia con: rm dashboard.pid${NC}"
    fi
else
    echo -e "${RED}❌ No se encontró dashboard.pid${NC}"
    echo -e "${YELLOW}El servidor no parece estar corriendo en segundo plano${NC}"
fi

echo ""

# 2. Verificar puerto 8000
echo -e "${BLUE}🔌 Verificando puerto 8000...${NC}"
if netstat -tuln 2>/dev/null | grep -q ":8000 " || ss -tuln 2>/dev/null | grep -q ":8000 "; then
    echo -e "${GREEN}✅ Puerto 8000 está en uso (servidor escuchando)${NC}"
else
    echo -e "${RED}❌ Puerto 8000 NO está en uso${NC}"
fi

echo ""

# 3. Probar conexión HTTP
echo -e "${BLUE}🌐 Probando conexión HTTP...${NC}"
if command -v curl &> /dev/null; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health 2>/dev/null)

    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✅ API respondiendo correctamente (HTTP $HTTP_STATUS)${NC}"

        # Obtener información de health
        echo -e "\n${BLUE}Estado de la API:${NC}"
        curl -s http://localhost:8000/api/health 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "No se pudo parsear JSON"
    else
        echo -e "${RED}❌ API no responde (HTTP $HTTP_STATUS)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  curl no está instalado, no se puede probar HTTP${NC}"
fi

echo ""

# 4. Mostrar últimas líneas del log
if [ -f "logs/dashboard.log" ]; then
    echo -e "${BLUE}📄 Últimas 10 líneas del log:${NC}"
    echo -e "${YELLOW}────────────────────────────────────────────────${NC}"
    tail -n 10 logs/dashboard.log
    echo -e "${YELLOW}────────────────────────────────────────────────${NC}"
else
    echo -e "${YELLOW}⚠️  No se encontró archivo de log${NC}"
fi

echo ""

# 5. Resumen de endpoints
echo -e "${BLUE}📚 Endpoints disponibles:${NC}"
echo -e "  ${GREEN}•${NC} Dashboard:     http://localhost:8000/"
echo -e "  ${GREEN}•${NC} Health Check:  http://localhost:8000/api/health"
echo -e "  ${GREEN}•${NC} Acciones:      http://localhost:8000/api/acciones"
echo -e "  ${GREEN}•${NC} Tasas:         http://localhost:8000/api/tasas/actual"
echo -e "  ${GREEN}•${NC} Documentación: http://localhost:8000/docs"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
