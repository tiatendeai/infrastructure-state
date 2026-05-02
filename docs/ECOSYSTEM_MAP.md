# 🗺️ Mapa do Ecossistema Ruptur

Este documento mapeia o ambiente atual a partir de `dev/` e serve como referência soberana para o **State** e para o **shipyard**.

## 🌲 Estrutura de Pastas (Hierarquia Atual)

```mermaid
graph TD
    Root["/Users/diego/dev"]

    Root --> RupturCloud["ruptur-cloud/"]
    RupturCloud --> RupturMain["ruptur-main/"]
    RupturMain --> Shipyard["shipyard/ (O Estaleiro)"]

    Shipyard --> Scripts["scripts/ (Runners e sync)"]
    Shipyard --> Kernel["kernel/ (State JSON)"]
    Shipyard --> Registry["registry/ (histórico e catálogos)"]
    Shipyard --> Adapters["adapters/ (Linear, Memory, GCP, IA)"]
    Shipyard --> Docs["docs/ (Runbooks, mapas e arquitetura)"]
    Shipyard --> Tasks["tasks/ (fila declarativa)"]
    Shipyard --> StateRuntime["state/runtime/ (HITL, sessões e snapshots)"]

    Root --> StateRepo["github.com/tiatendeai/state (memória canônica viva)"]
    Root --> RupturCloudLab["Ruptur Cloud Lab / GCP (runtime operacional)"]
    Root --> Obsidian["Obsidian + Excalidraw (mapas e visão rápida)"]
    Root --> RustyRDK["Rusty RDK (camada Rust de integração/SDK)"]

    Root --> Legacy["Legado: infrastructure-state, KVM2, Hostinger, Oracle"]
```

## 📜 Instruções de Navegação para Jarvis
1.  **Sempre** assumir o `shipyard/` como a raiz de qualquer instrução de infraestrutura.
2.  **Sempre** usar o `scripts/ruptur.sh` para operações automatizadas.
3.  **Sempre** validar no `kernel/state.json` antes de iniciar uma nova manobra.
4.  **Sempre** tratar `GCP` / `Ruptur Cloud Lab` como alvo operacional atual.
5.  **Sempre** tratar `KVM2` como legado, salvo quando o histórico exigir rastreabilidade.

---
*🧬 🧠 🦾 ⌬ ∞ | J.A.R.V.I.S. — State Architecture Map — 2026-04-20*
