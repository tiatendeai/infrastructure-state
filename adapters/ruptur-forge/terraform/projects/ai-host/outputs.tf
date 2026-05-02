output "ai_host_external_ip" {
  description = "IP externo da instância. Atualize ansible_host no inventário após o apply."
  value       = google_compute_instance.ai_host.network_interface[0].access_config[0].nat_ip
}

output "ai_host_internal_ip" {
  description = "IP interno do VPC. Use este valor em ai_host_ip no group_vars/all.yml para comunicação Jarvis → Ollama e AIOX → Ollama."
  value       = google_compute_instance.ai_host.network_interface[0].network_ip
}

output "ai_host_name" {
  value = google_compute_instance.ai_host.name
}

output "ai_host_zone" {
  value = google_compute_instance.ai_host.zone
}

output "ai_host_contract" {
  value = {
    service_name = "ai-host"
    workload     = "ollama"
    runtime      = var.gpu_enabled ? "gcp / debian-12 / n1-standard-16 + 1x t4" : "gcp / debian-12 / cpu-only"
    strategy     = "terraform_provisions_ansible_converges"
    governance   = "state"
    executor     = "shipyard"
    orchestrator = "jarvis"
    next_step    = var.gpu_enabled ? "Aguarde o startup-script estabilizar o driver NVIDIA (pode haver reboot), copie ai_host_internal_ip para ai_host_ip em group_vars/all.yml e execute: ansible-playbook playbooks/ai_host_gcp.yml" : "Copie ai_host_internal_ip para ai_host_ip em group_vars/all.yml e execute: ansible-playbook playbooks/ai_host_gcp.yml"
  }
}
