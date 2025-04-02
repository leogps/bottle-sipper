FROM python:3.12.9-alpine AS builder

WORKDIR /usr/src/app

COPY . .

RUN apk add --no-cache binutils py3-pip py3-setuptools py3-wheel musl-dev gcc libffi-dev \ 
    && pip install --upgrade pip && \
    pip install pyinstaller && \
    pip install -r requirements.txt && \
    pyinstaller sipper.py --clean --onefile --add-data sipper_core/templates/:sipper_core/templates/ --add-data static/:static/ --add-data sipper_core/:sipper_core/ --collect-submodules pkg_resources && \
    dist/sipper -h

# Use a minimal Alpine image for runtime
FROM alpine:latest

# Copy the compiled PyInstaller binary from the builder stage
COPY --from=builder /usr/src/app/dist/sipper /bin/sipper

# Set the entrypoint
ENTRYPOINT ["/bin/sipper"]
