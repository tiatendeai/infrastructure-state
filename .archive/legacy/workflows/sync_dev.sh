#!/usr/bin/env bash
# =============================================================================
# n8n_sync.sh — Sincroniza o workflow DEV local → n8n DEV (nuvem)
# Projeto: IA Jurídica Dr. Flávio (MVP)
# Regra: NUNCA sincronizar para PROD diretamente. Apenas DEV.
# =============================================================================

set -e

N8N_BASE_URL="https://n8n.atendezaya.com/api/v1"
N8N_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OWZjYzAxYi05OGRkLTQ5MjgtODY3My1kZmM1YzA1YTA1OGUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiM2IwMDI4MzQtNDNlZC00MDk0LWI4N2YtN2ZiODVhZTNjMGNlIiwiaWF0IjoxNzc0Nzk4MDQ3fQ._kVJB-46LH-vadiFKxmImtdjVDd0gemVZ8GDJqmpdNs"
DEV_WORKFLOW_ID="oZaITKQjdW4KnTf7"
LOCAL_FILE="$(dirname "$0")/dr_flavio_dev.json"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=================================================="
echo " 🚀 n8n Sync — Dr. Flávio DEV"
echo "=================================================="
echo ""

# Verificar se o arquivo local existe
if [ ! -f "$LOCAL_FILE" ]; then
  echo -e "${RED}❌ Arquivo local não encontrado: $LOCAL_FILE${NC}"
  exit 1
fi

echo -e "${YELLOW}📄 Arquivo:${NC} $LOCAL_FILE"
echo -e "${YELLOW}🎯 Destino:${NC} DEV ($DEV_WORKFLOW_ID) em $N8N_BASE_URL"
echo ""

# Confirmação de segurança
read -p "⚠️  Confirma o envio para n8n DEV? (s/N): " CONFIRM
if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
  echo -e "${YELLOW}⏹️  Operação cancelada.${NC}"
  exit 0
fi

echo ""
echo "📤 Enviando workflow..."

# Envia via PUT para o endpoint do n8n
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X PUT \
  "$N8N_BASE_URL/workflows/$DEV_WORKFLOW_ID" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @"$LOCAL_FILE")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  echo -e "${GREEN}✅ Sync concluído! HTTP $HTTP_CODE${NC}"
  echo ""
  echo "🔗 Verifique em: https://n8n.atendezaya.com/workflow/$DEV_WORKFLOW_ID"
else
  echo -e "${RED}❌ Erro HTTP $HTTP_CODE${NC}"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
  exit 1
fi

echo ""
