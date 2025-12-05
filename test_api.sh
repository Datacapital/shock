#!/bin/bash

# Script para probar todos los endpoints de la API

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🧪 Probando todos los endpoints de la API${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Función para probar un endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4

    echo -e "${YELLOW}Probando: $description${NC}"
    echo -e "${BLUE}$method $endpoint${NC}"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    fi

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅ OK (HTTP $http_code)${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -n 20
    else
        echo -e "${RED}❌ ERROR (HTTP $http_code)${NC}"
        echo "$body" | head -n 10
    fi

    echo ""
}

# 1. Health Check
test_endpoint "GET" "/api/health" "Health Check"

# 2. Página principal
echo -e "${YELLOW}Probando: Página principal${NC}"
echo -e "${BLUE}GET /${NC}"
http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/" 2>/dev/null)
if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✅ OK (HTTP $http_code)${NC}"
else
    echo -e "${RED}❌ ERROR (HTTP $http_code)${NC}"
fi
echo ""

# 3. Obtener acciones
test_endpoint "GET" "/api/acciones" "Obtener lista de acciones"

# 4. Obtener tasas actuales
test_endpoint "GET" "/api/tasas/actual" "Obtener tasas de cambio actuales"

# 5. Obtener configuración
test_endpoint "GET" "/api/config" "Obtener configuración del sistema"

# 6. Obtener resumen del mercado
test_endpoint "GET" "/api/resumen" "Obtener resumen del mercado"

# 7. Obtener última actualización
test_endpoint "GET" "/api/ultima-actualizacion" "Obtener info de última actualización"

# 8. Obtener precios BVC
test_endpoint "GET" "/api/precios/bvc?limit=5" "Obtener precios BVC (límite 5)"

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Pruebas completadas${NC}"
echo ""
echo -e "${YELLOW}Nota:${NC} Algunos endpoints pueden fallar si no hay datos en la base de datos"
echo -e "${YELLOW}      Para actualizar datos manualmente, ejecuta:${NC}"
echo -e "${BLUE}      curl -X POST http://localhost:8000/api/actualizar \\${NC}"
echo -e "${BLUE}           -H 'Content-Type: application/json' \\${NC}"
echo -e "${BLUE}           -d '{\"tarea\": \"todo\"}'${NC}"
echo ""
