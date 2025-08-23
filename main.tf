# Configuration du provider Docker
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.13.0"
    }
  }
}

provider "docker" {}

# Ressource pour l'image Docker
# Cela garantit que l'image est gérée par Terraform.
resource "docker_image" "recon_image" {
  name = "domain-recon-project:latest"
}

# Ressource Docker pour lancer le conteneur
resource "docker_container" "recon_tool" {
  name    = "recon-${var.domain_name}"
  image   = docker_image.recon_image.name

  command = ["python", "main.py", var.domain_name]

  must_run = false
  destroy_grace_seconds = 1
}