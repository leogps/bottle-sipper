# Define variables
DOCKER_IMAGE_NAME = leogps/bottle-sipper
DOCKER_TAG = 0.1.30
PLATFORMS = linux/amd64,linux/arm64,linux/arm/v7

# Phony targets to prevent conflicts with files of the same name
.PHONY: buildAndPush

# Build and push Docker image
buildAndPush: build
	docker buildx build --no-cache . \
	-t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) \
	--platform "$(PLATFORMS)" \
	--push
