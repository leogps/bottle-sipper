# Define variables
DOCKER_IMAGE_NAME = leogps/bottle-sipper
DOCKER_TAG = 0.1.32-1
PLATFORMS = linux/amd64,linux/arm64

# Phony targets to prevent conflicts with files of the same name
.PHONY: buildAndPush test clean

prepare:
	python -m venv .venv
	. .venv/bin/activate
	pip install -r requirements.txt

clean:
	rm -rf bottle_sipper.egg-info
	rm -rf build
	rm -rf dist

test: prepare
	python -m unittest discover test

# Build and push Docker image
buildAndPush:
	docker buildx build --no-cache . \
	-t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) \
	--platform "$(PLATFORMS)" \
	--push
