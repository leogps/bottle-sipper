# bottle-sipper

## Sipper is a simple, zero-configuration command-line static HTTP server. 

It is built using bottle: 
https://github.com/bottlepy/bottle | https://bottlepy.org/docs/dev/


---


It aims to provide the same value provided by `http-server` tool written in nodejs:
https://github.com/http-party/http-server | https://www.npmjs.com/package/http-server

---

### Usage

    # Pip based installation:
    python -m pip install bottle-sipper
    
#### Zero config run
    python -m sipper <directory-to-serve>

-- OR --

#### Run with 'media' template
    python -m sipper -t media <directory-to-serve>

-- OR --

#### Run with 'searchable' arg
    python -m sipper -q <directory-to-serve> # -t media ## to use media template.

---

#### Options
    
    usage: sipper.py [-h] [-d SHOW_DIR] [-a ADDRESS] [-p PORT] [-u USERNAME] [-P PASSWORD] [-b TEMPLATE_BASE_DIR] [-t USE_AVAILABLE_TEMPLATE] directory

    positional arguments:
    directory

    options:
    -h, --help            show this help message and exit
    -d SHOW_DIR, --show-dir SHOW_DIR. 
                           Show directory listings
    -a ADDRESS, --address ADDRESS. 
                           Address for the server, defaults to 0.0.0.0
    -p PORT, --port PORT  Port for the server
    -b TEMPLATE_BASE_DIR, --template-base-dir TEMPLATE_BASE_DIR. 
                          Template base directory. Takes precedence over --use-available-template option
    -t USE_AVAILABLE_TEMPLATE, --use-available-template 
                          USE_AVAILABLE_TEMPLATE. Use out-of-the-box templates. Available templates: default, media
    -q, --searchable      Add search box to be able to search on files (Performs fuzzy search similar to fzf tool).
    -g, --gzip            When enabled, it will server some-file.js.gz file in place of some-file.js when a gzipped version of the file exists and the request accepts gzip encoding.
                          Also applies gzip to the directory listing response.
    -s, --silent          Suppress log messages from output

    auth-options:
    -u USERNAME, --username USERNAME
                          Username for basic authentication
    -P PASSWORD, --password PASSWORD
                          Password for basic authentication

    ssl-options:
    -S, --ssl-enabled, --tls-enabled
                          Enable secure request serving with TLS/SSL (HTTPS).
    -C CERT, --cert CERT  Path to ssl cert file
    -K KEY, --key KEY     Path to ssl key file
---

#### Programmatical usage:
  
    sipper = Sipper('<dir>')
    sipper.start_sipping('0.0.0.0', 8080)

---

### Development

    python -m venv .venv # (Optional)
    pip install -r requirements.txt

---


### Custom templates
- Custom templates can be used overriding default templates by passing `-b or --template-base-dir` argument.
- The custom template supports [SimpleTemplate Engine](https://bottlepy.org/docs/dev/stpl.html) out-of-the-box.
- The following properties are available for use in the template:


      {
          "dir": "<current_directory>",
          "template_base_dir": "<template_base_dir>",
          "file_details_list": [{
            {
                "hash": "<hash_of_file_or_dir_within_parent_folder>",
                "isDir": <true/false>,
                "fileIconStyleClass": "<icon_style_class_for_file>",
                "fileIconBase64": "<base64_data_of_icon>",
                "lastModifiedDate": "<last_modified_date_formatted_as_string>",
                "filePermissions": "<file_permissions_formatted>",
                "fileSize": "<file_size_formatted>",
                "fileLink": "<file_url>",
                "fileName": "<file_name>"
            }
          }],
          "icons": [{
            "name": "<icon_name>",
            "base64_data": "<base64_data_icon>"
          }],
          "python_version": "<version_of_python>",
          "app_name": "<application_name>",
          "app_version": "<application_version>",
          "app_link": "<applicantion_link>",
          "server_address": "<address_of_server>",
          "searchable": <true/false>
      }

