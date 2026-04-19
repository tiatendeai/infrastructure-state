import fs from 'fs';
import { parseMermaidToExcalidraw } from '@excalidraw/mermaid-to-excalidraw';

const mermaidCode = `graph TD
    classDef genesis fill:#000000,stroke:#f00,stroke-width:3px,color:#fff;
    classDef governance fill:#1a1a2e,stroke:#0f3460,stroke-width:2px,color:#fff;
    classDef lifecycle fill:#16213e,stroke:#e94560,stroke-width:2px,color:#fff;
    classDef orchestrator fill:#0f3460,stroke:#e94560,stroke-width:3px,color:#fff;
    classDef execution fill:#005e54,stroke:#128c7e,stroke-width:2px,color:#fff;
    classDef saas fill:#ff9f43,stroke:#ee5253,stroke-width:2px,color:#fff;
    classDef infra fill:#34495e,stroke:#2c3e50,stroke-width:2px,color:#fff;
    classDef wapi fill:#25D366,stroke:#128c7e,stroke-width:2px,color:#000;

    subgraph Governo e Identidade
        Alpha["alpha (Gênese)"]:::genesis
        State["state (Governança)"]:::governance
        Omega["omega (Lifecycle)"]:::lifecycle
        InfraState["infrastructure-state"]:::infra
        VpsOracle["vps-oracle"]:::infra
    end

    subgraph Motores Core
        Jarvis["J.A.R.V.I.S."]:::orchestrator
        Ruptur["ruptur"]:::execution
        Farm["ruptur-farm"]:::execution
    end

    subgraph Produtos SaaS
        WDP["will-dados-pro"]:::saas
        WDPRobo["will-dados-pro-robo"]:::saas
        WDPMod["will-dados-pro-modular-desacoplado"]:::saas
        WDPTrain["will-dados-pro-the-training-room"]:::saas
        BetAI["plataforma-bet-ai"]:::saas
        RevEngine["ruptur-revenue-engine-os-ai"]:::saas
        Boost["tiatendeai-business-boost"]:::saas
        HappyMsg["happy-client-messager"]:::saas
        AutoClick["auto-click-bot"]:::execution
        Farm2DL["2dl-automated-tech-farm"]:::saas
        StatusP["statuspersianas"]:::saas
        Zaya["zaya"]:::saas
        Bolinhas["bolinhas"]:::saas
        CaboWaves["cabo-frio-waves"]:::saas
        CaboEm["cabo-wave-embrace"]:::saas
    end

    subgraph Cognição
        Cognitive["ruptur-cognitive-growth-machine"]:::execution
        SelfEvol["caes-for-self-evolution-system"]:::execution
        SafeFlow["safe-flow-ia"]:::execution
        Context7["context7"]:::execution
        Skills["ruptur-skills"]:::execution
        Antigrav["antigravity-kit"]:::execution
        AntigravSkills["antigravity-awesome-skills"]:::execution
        Prompts["ruptur-prompts"]:::execution
        HistBruto["historicos-brutos-de-ia"]:::execution
        Whisper["connect-client-whisper"]:::execution
        SetupAi["Setup-Ai"]:::execution
        ADK["adk"]:::execution
    end

    subgraph Gateways WA
        Uazapi["uazapi"]:::wapi
        Baileys["ruptur-baileys"]:::wapi
        WapiApp["wapi"]:::wapi
        AgentKit["whatsapp-agentkit"]:::wapi
        ZapFlow["zapflowai"]:::wapi
    end

    Alpha --> State
    State --> InfraState
    InfraState --> VpsOracle
    State --> Jarvis
    Omega --> Jarvis
    
    Jarvis --> Ruptur
    Jarvis --> Farm

    Ruptur --> RevEngine
    Ruptur --> WDP
    Ruptur --> BetAI
    Ruptur --> Zaya
    Ruptur --> CaboWaves
    CaboWaves --> CaboEm

    WDPRobo --> WDP
    WDPMod --> WDP
    WDPTrain --> WDP

    Cognitive --> Jarvis
    Cognitive --> HistBruto
    SelfEvol --> Ruptur
    Skills --> Jarvis
    Antigrav --> Jarvis
    AntigravSkills --> Antigrav
    Prompts --> Jarvis
    Context7 --> Jarvis
    Whisper --> Jarvis
    InfraState --> SetupAi
    Jarvis --> ADK

    Uazapi --> Jarvis
    Baileys --> Uazapi
    WapiApp --> Uazapi
    AgentKit --> Uazapi
    ZapFlow --> Uazapi

    Farm --> Farm2DL
    Farm --> AutoClick
    RevEngine --> HappyMsg
    RevEngine --> Boost
`;

async function convert() {
  try {
    const excalidrawScene = await parseMermaidToExcalidraw(mermaidCode, { fontSize: 20 });
    const payload = {
        type: "excalidraw",
        version: 2,
        source: "https://excalidraw.com",
        elements: excalidrawScene.elements,
        appState: { viewBackgroundColor: "#ffffff", theme: "light" },
        files: excalidrawScene.files
    };
    fs.writeFileSync('ecossistema.excalidraw', JSON.stringify(payload, null, 2));
    console.log("SUCESSO: Arquivo ecossistema.excalidraw gerado!");
  } catch (err) {
    console.error("ERRO: ", err);
  }
}

convert();
