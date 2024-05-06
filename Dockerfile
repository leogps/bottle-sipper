FROM python:3.11.9-bullseye as builder

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip
RUN pip install pyinstaller
RUN pip install -r requirements.txt
RUN pyinstaller sipper.py --clean --onefile --add-data sipper_core/templates/:sipper_core/templates/ --add-data static/:static/ --add-data sipper_core/:sipper_core/ --collect-submodules pkg_resources
RUN dist/sipper -h

FROM debian:bookworm-slim

COPY --from=builder /usr/src/app/dist/sipper /bin/sipper
ENTRYPOINT ["/bin/sipper"]
