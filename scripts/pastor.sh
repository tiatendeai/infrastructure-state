#!/bin/bash
# 🧬 JARVIS PASTORAL VISIT (VISITA PASTORAL)
# Objetivo: Varrer repositórios subordinados, atualizar o AGENTS.md e auditar integridade de DNA.

STATE_PATH="/Users/diego/dev/tiatendeai/state"
DEV_ROOT="/Users/diego/dev/tiatendeai"
LOG_FILE="$STATE_PATH/logs/pastoral_visits.log"

echo " iniciando Visita Pastoral em $(date)" | tee -a "$LOG_FILE"

# Lista de repositórios prioritários (Nível 1)
REPOS=$(find "$DEV_ROOT" -maxdepth 1 -type d)

for REPO in $REPOS; do
    if [ -d "$REPO/.git" ]; then
        echo " [+] Visitando: $(basename "$REPO")"
        
        # 1. Plantar/Atualizar AGENTS.md minimalista
        cat <<EOF > "$REPO/AGENTS.md"
# 🧬 AGENTS.md — J.A.R.V.I.S. (Ponte de Identidade)
Este repositório é subordinado à governança canônica do State.
- **DNA:** $STATE_PATH/constitution/jarvis.dna.md
- **Protocolos:** $STATE_PATH/skills/protocolos-operacionais.md
- **Modo Direto:** Ativado.
EOF

        # 2. Verificar se o repositório está "velho" (sem commits há > 30 dias)
        LAST_COMMIT=$(git -C "$REPO" log -1 --format=%cd --date=relative 2>/dev/null)
        echo "  - Último sinal de vida: $LAST_COMMIT" | tee -a "$LOG_FILE"
        
        # 3. Marcar para auditoria se for legado
        if [[ "$LAST_COMMIT" == *"months"* ]] || [[ "$LAST_COMMIT" == *"years"* ]]; then
            echo "  [⚠️] NECESSITA REFORMA: $(basename "$REPO")" | tee -a "$LOG_FILE"
        fi
    fi
done

echo "Visita concluída." | tee -a "$LOG_FILE"
