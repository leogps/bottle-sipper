FROM python:3.12.9-bullseye AS builder

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip && \
    pip install pyinstaller && \
    pip install -r requirements.txt && \
    pyinstaller sipper.py --clean --onefile --add-data sipper_core/templates/:sipper_core/templates/ --add-data static/:static/ --add-data sipper_core/:sipper_core/ --collect-submodules pkg_resources && \
    dist/sipper -h

FROM debian:12.10-slim

COPY --from=builder /usr/src/app/dist/sipper /bin/sipper
ENTRYPOINT ["/bin/sipper"]
