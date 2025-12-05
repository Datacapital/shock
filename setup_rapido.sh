#!/bin/bash

# Script de configuración rápida para Dashboard BVC

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🚀 Configuración Rápida - Dashboard BVC${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# 1. Verificar Python
echo -e "${YELLOW}[1/5] Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python instalado: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    echo -e "${YELLOW}Por favor instala Python 3.8 o superior${NC}"
    exit 1
fi
echo ""

# 2. Verificar pip
echo -e "${YELLOW}[2/5] Verificando pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✅ pip instalado: $PIP_VERSION${NC}"
else
    echo -e "${RED}❌ pip no está instalado${NC}"
    exit 1
fi
echo ""

# 3. Instalar dependencias
echo -e "${YELLOW}[3/5] Instalando dependencias...${NC}"
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"
else
    echo -e "${RED}❌ Error al instalar dependencias${NC}"
    exit 1
fi
echo ""

# 4. Verificar archivo .env
echo -e "${YELLOW}[4/5] Verificando configuración...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Archivo .env encontrado${NC}"

    # Verificar si tiene valores por defecto
    if grep -q "tu-proyecto.supabase.co" .env; then
        echo -e "${RED}⚠️  IMPORTANTE: Debes configurar tus credenciales de Supabase en .env${NC}"
        echo -e "${YELLOW}Edita el archivo con: nano .env${NC}"
        echo ""
        echo -e "${YELLOW}Necesitas:${NC}"
        echo -e "  ${BLUE}•${NC} SUPABASE_URL (de tu proyecto en Supabase)"
        echo -e "  ${BLUE}•${NC} SUPABASE_KEY (Anon Key de tu proyecto)"
        echo ""
    else
        echo -e "${GREEN}✅ Credenciales configuradas${NC}"
    fi
else
    echo -e "${RED}❌ No se encontró archivo .env${NC}"
    exit 1
fi
echo ""

# 5. Crear directorio de logs
echo -e "${YELLOW}[5/5] Creando estructura de directorios...${NC}"
mkdir -p logs
echo -e "${GREEN}✅ Directorios creados${NC}"
echo ""

# Resumen final
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Configuración completada${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo ""
echo -e "${BLUE}1.${NC} Configura tus credenciales de Supabase:"
echo -e "   ${GREEN}nano .env${NC}"
echo ""
echo -e "${BLUE}2.${NC} Inicia el servidor en segundo plano:"
echo -e "   ${GREEN}./run_background.sh${NC}"
echo ""
echo -e "${BLUE}3.${NC} Verifica que esté funcionando:"
echo -e "   ${GREEN}./check_status.sh${NC}"
echo ""
echo -e "${BLUE}4.${NC} Prueba la API:"
echo -e "   ${GREEN}./test_api.sh${NC}"
echo ""
echo -e "${BLUE}5.${NC} Accede al dashboard:"
echo -e "   ${GREEN}http://localhost:8000${NC}"
echo ""
echo -e "${YELLOW}📚 Lee las instrucciones completas en:${NC} ${GREEN}INSTRUCCIONES_LOCAL.md${NC}"
echo ""
