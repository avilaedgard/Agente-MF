#!/bin/bash
# Script de configuração para GitHub Pages + Railway/Render

echo "🚀 VIGILANTE - Deploy Script"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Preparando repositório Git...${NC}"
git init
git add .
git commit -m "Initial commit - VIGILANTE v1.0"

echo -e "${BLUE}2. Qual é sua URL do Railway/Render?${NC}"
read API_URL
echo "API_URL=$API_URL" > .env.production

echo -e "${BLUE}3. Qual é seu usuário GitHub?${NC}"
read GITHUB_USER

echo -e "${BLUE}4. Qual é o nome do repositório?${NC}"
read REPO_NAME

echo -e "${GREEN}Próximos passos:${NC}"
echo ""
echo "1. No GitHub, crie um repositório: $REPO_NAME"
echo "   https://github.com/new"
echo ""
echo "2. Push do código:"
echo "   git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. No Railway/Render:"
echo "   - Conecte seu repositório"
echo "   - Defina variável de ambiente: API_ENDPOINT=$API_URL"
echo "   - Deploy automático ativado"
echo ""
echo "4. Configure GitHub Pages:"
echo "   - Settings > Pages"
echo "   - Build and deployment: GitHub Actions"
echo "   - Branch: main (/root ou /frontend)"
echo ""
echo -e "${GREEN}✓ Pronto para deploy!${NC}"
