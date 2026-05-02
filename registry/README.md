# Registry

Contém artefatos de execução gerados automaticamente.

- `registry/runs/`: registros por execução
- `registry/services.yaml`: visão observada dos serviços materializada a partir de inventários válidos e do alvo atual Ruptur Cloud Lab / GCP
- `registry/cloudflare-dns-targets.yaml`: estado desejado dos records de DNS enquanto a escrita no Cloudflare estiver bloqueada
- `registry/ai-license-control.yaml`: controle canônico de contas/licenças/credits dos agentes e ferramentas de IA
- `Infisical`: chaveiro canônico do Shipyard para segredos, tokens e chaves; Git carrega apenas contratos e referências, nunca valores sensíveis
- `Terraform` e `Ansible`: ferramentas canônicas de provisionamento e configuração do ambiente
