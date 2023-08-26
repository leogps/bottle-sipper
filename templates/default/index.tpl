<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html>
        <head>
            <title>Index of {{dir}}</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans-serif;}
              body {background-color: #fff; border: 1px solid #ddd;
                    padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
              table tr { white-space: nowrap; }
              td.perms {}
              td.file-size { text-align: right; padding-left: 1em; }
              td.display-name { padding-left: 1em; }
              i.icon { 
                display: block;
                height: 16px;
                width: 16px; 
              }

              % for icon in icons:
                i.icon-{{icon.name}} {
                  background-image: url("data:img/png;base64,{{icon.base64_data}}")
                }
              % end

              div.footer {
                margin-top: 2em;
                bottom: 0;
              }
            </style>
        </head>
        <body>
            <h1>Index of {{dir}}</h1>
            <table>
              <tbody>
                % for row in rows:
                    % include(row_template_file)
                % end
              </tbody>
            </table>
            <div class="footer">
                Python {{python_version}}/ <a href="{{app_link}}">{{app_name}}</a> server running @ {{server_address}}
            </div>
        </body>
    </html>

