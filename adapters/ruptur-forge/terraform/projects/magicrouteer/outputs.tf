output "magicrouteer_contract" {
  value = {
    service_name = var.service_name
    runtime      = "gcp + ollama"
    strategy     = "terraform_provisions_ansible_converges"
    governance   = "state"
    executor     = "shipyard"
    orchestrator = "jarvis"
  }
}
