
<!DOCTYPE html>
<html>
<head>
    <title>Index of {{dir}}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }

        h1.title {
            text-align: center;
        }

        .container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }

        .card {
            display: flex;
            align-items: center;
            background-color: #fff;
            box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.2);
            margin-bottom: 10px;
            padding: 10px;
        }

        a {
            text-decoration: none;
            color: none;
        }

        div.icon {
            width: 80px;
            height: 80px;
            color: #fff;
            font-size: 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 50%;
            margin-right: 10px;
            background-color: #cfcfcf;
        }

        .details {
            flex-grow: 1;
        }

        h2 {
            margin: 0;
            font-size: 20px;
            color: black;
        }

        p {
            margin: 5px 0;
            font-size: 14px;
            color: #777;
        }

        @media screen and (max-width: 600px) {
            .container {
                width: 100%;
                padding: 0;
            }

            .card {
                flex-direction: column;
                align-items: flex-start;
                padding: 15px;
            }

            .icon {
                width: 60px;
                height: 60px;
                font-size: 24px;
                margin-right: 0;
                margin-bottom: 10px;
            }

            .details {
                text-align: left;
            }

            h2 {
                font-size: 18px;
            }
        }

        div.icon i.file {
            width: 16px;
            height: 16px;
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }

        % for icon in icons:
          div.icon i.icon-{{icon.name}} {
            background-image: url("data:img/png;base64,{{icon.base64_data}}");
          }
        % end

        div.footer {
          margin-top: 2em;
          bottom: 0;
          padding: 10px;
        }
    </style>
</head>
<body>
    <h1 class="title">Index of {{dir}}</h1>
    <div class="container">
        % for row in rows:
          % include(row_template_file)
        % end
    </div>
    <div class="footer">
        Python {{python_version}}/ <a href="{{app_link}}">{{app_name}}</a> server running @ {{server_address}}
    </div>
</body>
</html>
