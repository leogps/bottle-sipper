# Define variables
DOCKER_IMAGE_NAME = leogps/bottle-sipper
DOCKER_TAG = 0.1.31-2
PLATFORMS = linux/amd64,linux/arm64

# Phony targets to prevent conflicts with files of the same name
.PHONY: buildAndPush

# Build and push Docker image
buildAndPush:
	docker buildx build --no-cache . \
	-t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) \
	--platform "$(PLATFORMS)" \
	--push
