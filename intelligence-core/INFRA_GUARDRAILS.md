# 🛡️ Guardrails de Infraestrutura (Ruptur-Cloud Native)

Diretrizes para a migração total e soberania no GCP.

## ☁️ Estratégia Cloud (Ruptur-Cloud)
1. **Namespace Ruptur:** Abandonar progressivamente o termo `tiatendeai` em prol de `ruptur-cloud`. No GCP, tudo nasce 100% Ruptur.
2. **Prioridade GCP:** Novos serviços devem nascer no GCP para garantir integração nativa.
3. **Containerização (A Turminha no Cloud):** Jarvis, Ruptur e os Agentes devem ser preparados para rodar em Cloud Run ou GKE (Kubernetes), garantindo escala e failover.
4. **SaaS-First:** Sempre que possível, usar Cloudflare Workers ou Vercel Edge para reduzir latência e custo.
5. **Backup CCT:** O `infrastructure-state` deve ter espelhamento cross-cloud (GCP + GitHub) para evitar o "Apagão de Verdade".

## 🚧 Política de Caos (Chaos)
- **Latência:** Testar periodicamente o comportamento do Ruptur sob alta latência na Hostinger.
- **Failover:** O sistema deve saber migrar o papel de "Gate" do Jarvis para um container reserva no GCP se o ponto principal falhar.

## 🧹 Manutenção
- **Desmonte Oracle:** Avaliar se vale a pena manter a máquina Oracle apenas para um nó de "Testemunho" do CCT ou se devemos desligar.
