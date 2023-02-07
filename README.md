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
    
    
    usage: sipper.py [-h] [-d DIR] [-a ADDRESS] [-p PORT] directory

    positional arguments:
    directory

    options:
      -h, --help            show this help message and exit
      -d DIR, --dir DIR     Show directory listings
      -a ADDRESS, --address ADDRESS
                            Address for the server, defaults to 0.0.0.0
      -p PORT, --port PORT  Port for the server

