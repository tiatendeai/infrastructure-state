variable "gcp_project_id" {
  description = "Projeto GCP onde o host de IA será materializado."
  type        = string
  default     = "ruptur-jarvis-v1-68358"
}

variable "gcp_region" {
  description = "Região canônica do runtime do AI Host."
  type        = string
  default     = "southamerica-east1"
}

variable "gcp_zone" {
  description = "Zona canônica do runtime do AI Host. Em São Paulo, T4 está disponível em southamerica-east1-a e southamerica-east1-c."
  type        = string
  default     = "southamerica-east1-c"
}

variable "instance_name" {
  description = "Nome canônico da instância."
  type        = string
  default     = "ruptur-ai-host-01"
}

variable "machine_type" {
  description = "Tipo de máquina GCP. n1-standard-16 é o baseline recomendado para o host dedicado de IA com 1x T4."
  type        = string
  default     = "n1-standard-16"
}

variable "disk_size_gb" {
  description = "Tamanho do disco de boot em GB. 200 GB acomoda Ollama, drivers NVIDIA e múltiplos modelos quantizados com folga operacional."
  type        = number
  default     = 200
}

variable "disk_type" {
  description = "Tipo de disco de boot. pd-ssd reduz latência de carga de modelos e warmup do runtime."
  type        = string
  default     = "pd-ssd"
}

variable "boot_image" {
  description = "Imagem base da instância. Debian 12 é o baseline suportado pela automação de driver GPU do Compute Engine."
  type        = string
  default     = "debian-cloud/debian-12"
}

variable "gpu_enabled" {
  description = "Anexa GPU ao host dedicado. Mantido true por padrão para o baseline de inferência local."
  type        = bool
  default     = true
}

variable "gpu_type" {
  description = "Tipo de GPU anexada ao host quando gpu_enabled=true."
  type        = string
  default     = "nvidia-tesla-t4"
}

variable "gpu_count" {
  description = "Quantidade de GPUs anexadas ao host."
  type        = number
  default     = 1
}

variable "ssh_source_ranges" {
  description = "CIDRs autorizados a abrir SSH no AI Host. Restrinja para o /32 do operador antes do apply quando possível."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ssh_user" {
  description = "Usuário SSH injetado nos metadados da instância."
  type        = string
  default     = "diego"
}

variable "ssh_pub_key_path" {
  description = "Caminho local da chave pública SSH que será injetada na instância."
  type        = string
  default     = "~/.ssh/google_compute_engine.pub"
}
