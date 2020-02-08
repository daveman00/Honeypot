
class HTTPServerSettings:
    # address of the server; blank will bind to all interfaces
    bind_address = "0.0.0.0"
    # port of the HTTPService service
    server_port = 80
    # directory with html pages
    pages_dir = "Honeypot/Services/HTTPService/html"
    # names of the pages to be served; the first one existing will be served
    main_pages = ["index.html", "index.htm", "main.html", "main.htm", "home.html", "home.htm"]
    # the HTTPService server version
    server_version = "Apache 2.4.27"
    # timeout setting
    timeout = 200
    # system version
    system_version = "Debian"
    # protocol version; set to HTTPService/1.1 to enable automatic keepalive
    protocol_version = "HTTP/1.0"

