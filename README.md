# bottle-sipper

## Sipper is a simple, zero-configuration command-line static HTTP server. 

It is built using bottle: 
https://github.com/bottlepy/bottle | https://bottlepy.org/docs/dev/


---


It aims to provide the same value provided by `http-server` tool written in nodejs:
https://github.com/http-party/http-server | https://www.npmjs.com/package/http-server

---

### Development

    python -m venv .venv # (Optional)
    pip install -r requirements.txt

---

### Usage
  
    sipper = Sipper('<dir>')
    sipper.start_sipping('0.0.0.0', 8080)

--- 
    
    
    usage: sipper.py [-h] [-d SHOW_DIR] [-a ADDRESS] [-p PORT] [-u USERNAME] [-P PASSWORD] [-b TEMPLATE_BASE_DIR] [-t USE_AVAILABLE_TEMPLATE] directory

    positional arguments:
    directory

    options:
    -h, --help            show this help message and exit
    -d SHOW_DIR, --show-dir SHOW_DIR. Show directory listings
    -a ADDRESS, --address ADDRESS. Address for the server, defaults to 0.0.0.0
    -p PORT, --port PORT  Port for the server
    -u USERNAME, --username USERNAME. Username for basic authentication
    -P PASSWORD, --password PASSWORD. Password for basic authentication
    -b TEMPLATE_BASE_DIR, --template-base-dir TEMPLATE_BASE_DIR. Template base directory. Takes precedence over --use-available-template option
    -t USE_AVAILABLE_TEMPLATE, --use-available-template USE_AVAILABLE_TEMPLATE. Use out-of-the-box templates. Available templates: default, media

---

    # Pip based installation:
    python -m pip install bottle-sipper
    
    # No-config run:
    python -m sipper <directory-to-serve>

    # Run with existing 'media' template
    python -m sipper -t media <directory-to-serve>
