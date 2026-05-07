terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "punaconnect-bot-555"
  region  = "us-central1"
  zone    = "us-central1-a"
}

resource "google_compute_instance" "punaconnect_vm" {
  name         = "punaconnect-vm"
  machine_type = "e2-micro"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
      size  = 30
      type  = "pd-standard"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    startup-script = <<-EOT
      #!/bin/bash
      # Utilizar alpine/git para clonar el repositorio ya que COS no tiene git nativo
      docker run --rm -v /tmp:/tmp alpine/git clone https://github.com/Fernandofarfan/PunaConnect.git /tmp/PunaConnect
      
      # Construir el contenedor
      cd /tmp/PunaConnect
      docker build -t punaconnect-bot .
      
      # Ejecutar el contenedor del bot
      docker run -d --name punabot \
        --restart unless-stopped \
        -e TELEGRAM_TOKEN="8489865382:AAGV1o04ODRQkzj5fixU_rQs1iJ3vlHxaUU" \
        punaconnect-bot
    EOT
  }

  tags = ["punaconnect-bot"]
}
