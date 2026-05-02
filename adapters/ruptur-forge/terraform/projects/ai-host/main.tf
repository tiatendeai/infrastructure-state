locals {
  ssh_key_entry = "${var.ssh_user}:${file(pathexpand(var.ssh_pub_key_path))}"

  gpu_driver_startup_script = <<-EOT
    #!/bin/bash
    set -euxo pipefail

    if test -f /opt/google/cuda-installer/cuda_installation; then
      exit 0
    fi

    mkdir -p /opt/google/cuda-installer
    cd /opt/google/cuda-installer

    curl -fSsL -O https://storage.googleapis.com/compute-gpu-installation-us/installer/latest/cuda_installer.pyz
    python3 cuda_installer.pyz install_cuda || true

    if command -v nvidia-smi >/dev/null 2>&1; then
      touch /opt/google/cuda-installer/cuda_installation
    fi
  EOT
}

# -----------------------------------------------------------------------
# Instância dedicada ao runtime de IA (Ollama)
# -----------------------------------------------------------------------
resource "google_compute_instance" "ai_host" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = var.boot_image
      size  = var.disk_size_gb
      type  = var.disk_type
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata = {
    ssh-keys = local.ssh_key_entry
  }

  metadata_startup_script = var.gpu_enabled ? local.gpu_driver_startup_script : null

  # ruptur-ai-host: alvo das regras de firewall para Ollama e SSH
  tags = ["ruptur-ai-host"]

  labels = {
    service     = "ai-host"
    workload    = "ollama"
    environment = "production"
    managed_by  = "terraform"
  }

  dynamic "guest_accelerator" {
    for_each = var.gpu_enabled ? [1] : []
    content {
      type  = var.gpu_type
      count = var.gpu_count
    }
  }

  scheduling {
    on_host_maintenance = var.gpu_enabled ? "TERMINATE" : "MIGRATE"
    automatic_restart   = true
  }

  shielded_instance_config {
    enable_secure_boot = false
  }
}

# -----------------------------------------------------------------------
# Firewall — Ollama (11434) acessível apenas pela rede interna do VPC
# Isso garante que ruptur-shipyard-01 alcança o Ollama via IP interno,
# mas o serviço não fica exposto na internet.
# -----------------------------------------------------------------------
resource "google_compute_firewall" "ollama_internal" {
  name    = "ruptur-ollama-internal"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["11434"]
  }

  # RFC 1918 — cobre toda a rede interna do projeto GCP
  source_ranges = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  target_tags   = ["ruptur-ai-host"]

  description = "Permite acesso ao Ollama (11434) apenas a partir da rede interna GCP."
}

# -----------------------------------------------------------------------
# Firewall — SSH (22) para gerenciamento via Ansible / gcloud
# -----------------------------------------------------------------------
resource "google_compute_firewall" "ai_host_ssh" {
  name    = "ruptur-ai-host-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = var.ssh_source_ranges
  target_tags   = ["ruptur-ai-host"]

  description = "Permite SSH ao AI Host para provisionamento via Ansible. Restrinja os CIDRs antes do apply."
}
