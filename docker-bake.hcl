variable "IMAGE" {
  default = "ghcr.io/AlphaSphereDotAI/chatacter_backend_app"
}
target "default" {
  name = "chatacter_backend_app"
	context = .
  tags = [ "${IMAGE}:dev", "${IMAGE}:latest" ]
  dockerfile = "Dockerfile"
  platforms = [ "linux/amd64", "linux/arm64" ]
}
