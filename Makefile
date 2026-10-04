# Define variables
DOCKER_IMAGE_NAME = leogps/bottle-sipper
DOCKER_TAG = 0.1.31-5
PLATFORMS = linux/amd64,linux/arm64

# Phony targets to prevent conflicts with files of the same name
.PHONY: buildAndPush test

prepare:
	python -m venv .venv
	. .venv/bin/activate
	pip install -r requirements.txt

test: prepare
	python -m unittest discover test

# Build and push Docker image
buildAndPush:
	docker buildx build --no-cache . \
	-t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) \
	--platform "$(PLATFORMS)" \
	--push
