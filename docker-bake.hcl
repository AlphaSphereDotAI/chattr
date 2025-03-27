variable "IMAGE" {
  default = "ghcr.io/alphaspheredotai/chatacter_backend_app"
}

target "default" {
  context    = "."
  tags       = ["${IMAGE}:dev", "${IMAGE}:latest"]
  dockerfile = "Dockerfile"
  platforms  = ["linux/amd64", "linux/arm64"]
  labels = {
    "org.opencontainers.image.source" = "https://github.com/AlphaSphereDotAI/chatacter_backend_app"
  }
  cache_from = [{ type = "gha" }]
  cache_to = [
    {
      type = "gha"
      mode = "max"
    }
  ]
  output = [{ type = "registry" }]
}
