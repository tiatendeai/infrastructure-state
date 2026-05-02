variable "gcp_project_id" {
  description = "Projeto GCP onde o MagicRouteer será materializado."
  type        = string
}

variable "gcp_region" {
  description = "Região canônica do runtime do MagicRouteer."
  type        = string
  default     = "southamerica-east1"
}

variable "gcp_zone" {
  description = "Zona canônica do runtime do MagicRouteer."
  type        = string
  default     = "southamerica-east1-b"
}

variable "service_name" {
  description = "Identificador canônico do serviço."
  type        = string
  default     = "magicrouteer"
}
