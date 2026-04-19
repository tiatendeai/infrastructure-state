#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import json
from pathlib import Path

# Configurações de Path
ROOT = Path(__file__).resolve().parents[1]
ANSIBLE_DIR = ROOT / "adapters" / "provisioning" / "ansible"

def main():
    parser = argparse.ArgumentParser(description="Wrapper do Ansible para o Ruptur Farm Framework")
    parser.add_argument("playbook", help="Nome do playbook dentro da pasta playbooks/")
    parser.add_argument("--inventory", default="production", help="Nome do inventário")
    parser.add_argument("--extra-vars", help="JSON com variáveis extras")
    
    args = parser.parse_args()
    
    playbook_path = ANSIBLE_DIR / "playbooks" / args.playbook
    inventory_path = ANSIBLE_DIR / "inventories" / args.inventory / "hosts.yml"
    
    if not playbook_path.exists():
        print(f"Erro: Playbook não encontrado: {playbook_path}")
        sys.exit(1)
        
    command = [
        "ansible-playbook",
        str(playbook_path),
        "-i", str(inventory_path)
    ]
    
    if args.extra_vars:
        command.extend(["--extra-vars", args.extra_vars])
        
    # Execução
    # Definindo ANSIBLE_CONFIG para garantir que use o cfg local
    env = os.environ.copy()
    env["ANSIBLE_CONFIG"] = str(ANSIBLE_DIR / "ansible.cfg")
    
    result = subprocess.run(command, capture_output=True, text=True, cwd=str(ANSIBLE_DIR), env=env)
    
    output = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
        "playbook": args.playbook
    }
    
    print(json.dumps(output))
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
