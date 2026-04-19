# 🛡️ Guardrails de Infraestrutura (GCP First)

Diretrizes para manter o sistema imune e antifrágil.

## ☁️ Estratégia Cloud
1. **Prioridade GCP:** Novos serviços devem nascer no GCP para garantir integração nativa com o ecossistema de dados.
2. **SaaS-First:** Sempre que possível, usar Cloudflare Workers ou Vercel Edge para reduzir latência e custo.
3. **Backup CCT:** O `infrastructure-state` deve ter espelhamento cross-cloud (GCP + GitHub) para evitar o "Apagão de Verdade".

## 🚧 Política de Caos (Chaos)
- **Latência:** Testar periodicamente o comportamento do Ruptur sob alta latência na Hostinger.
- **Failover:** O sistema deve saber migrar o papel de "Gate" do Jarvis para um container reserva no GCP se o ponto principal falhar.

## 🧹 Manutenção
- **Desmonte Oracle:** Avaliar se vale a pena manter a máquina Oracle apenas para um nó de "Testemunho" do CCT ou se devemos desligar.
