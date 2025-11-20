#!/bin/bash
# ============================================
# Script para verificar el estado de Git en el servidor
# Ejecutar directamente en el servidor
# ============================================

# Configuración (ajustar según tu servidor)
SERVIDOR_RUTA="/var/www/gnv-app"
BRANCH="developer"

echo "============================================"
echo "  VERIFICAR ESTADO GIT EN EL SERVIDOR"
echo "============================================"
echo ""

# Verificar si existe repositorio git
echo "[1] Verificando si existe repositorio Git..."
cd "$SERVIDOR_RUTA" || {
    echo "  ERROR: No se puede acceder al directorio: $SERVIDOR_RUTA"
    exit 1
}

if ! git status > /dev/null 2>&1; then
    echo "  ERROR: No se encuentra un repositorio Git en $SERVIDOR_RUTA"
    exit 1
fi
echo "  OK: Repositorio Git encontrado"
echo ""

# Estado del repositorio
echo "[2] Estado del repositorio:"
git status
echo ""

# Branch actual
echo "[3] Branch actual:"
git branch --show-current
echo ""

# Últimos commits
echo "[4] Últimos 5 commits:"
git log --oneline -5
echo ""

# Información del commit actual
echo "[5] Información del commit actual (HEAD):"
git log -1 --pretty=format:'Hash: %H%nAutor: %an <%ae>%nFecha: %ad%nMensaje: %s' --date=format:'%Y-%m-%d %H:%M:%S'
echo ""
echo ""

# Verificar si hay cambios sin commitear
echo "[6] Verificando cambios sin commitear:"
git diff --stat
echo ""

# Verificar estado con remoto
echo "[7] Estado con el remoto (origin/$BRANCH):"
git fetch origin --quiet
git status -sb
echo ""

# URL del remoto
echo "[8] URL del repositorio remoto:"
git remote get-url origin
echo ""

# Comparar commits local vs remoto
echo "[9] Comparación con remoto:"
echo "Commits locales no en remoto:"
git log origin/$BRANCH..HEAD --oneline
echo ""
echo "Commits remotos no en local:"
git log HEAD..origin/$BRANCH --oneline
echo ""

echo "============================================"
echo "  VERIFICACIÓN COMPLETA"
echo "============================================"
echo ""

