#!/bin/bash

# Configurações do n8n (AtendeZaya)
N8N_API_URL="https://n8n.atendezaya.com/api/v1"
N8N_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3OWZjYzAxYi05OGRkLTQ5MjgtODY3My1kZmM1YzA1YTA1OGUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiM2IwMDI4MzQtNDNlZC00MDk0LWI4N2YtN2ZiODVhZTNjMGNlIiwiaWF0IjoxNzc0Nzk4MDQ3fQ._kVJB-46LH-vadiFKxmImtdjVDd0gemVZ8GDJqmpdNs"

# Função para dar o deploy (Update) de um workflow
deploy_workflow() {
    WORKFLOW_ID=$1
    FILE_PATH=$2

    if [ -z "$WORKFLOW_ID" ] || [ -z "$FILE_PATH" ]; then
        echo "Uso: ./scripts/n8n_sync.sh <workflow_id> <caminho_do_arquivo>"
        return 1
    fi

    echo "Subindo alterações para o Workflow ID: $WORKFLOW_ID..."
    
    # Faz o PUT para atualizar o workflow
    curl -X PUT "$N8N_API_URL/workflows/$WORKFLOW_ID" \
         -H "X-N8N-API-KEY: $N8N_API_KEY" \
         -H "Content-Type: application/json" \
         -d @"$FILE_PATH"

    echo -e "\nDeploy concluído!"
}

# Verifica argumentos
if [ "$1" == "deploy" ]; then
    deploy_workflow "$2" "$3"
else
    echo "Comandos disponíveis:"
    echo "  deploy <id> <arquivo>  - Sobe o JSON local para o n8n"
fi
