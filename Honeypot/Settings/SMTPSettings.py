
class SMTPServerSettings:
    # address of the server; present binds to all interfaces
    bind_address = "0.0.0.0"
    # port of the SMTPService service
    server_port = 25
    # fully qualified domain name
    fqdn = "DB6PR0022.mydomain.com"
    # the SMTPService server version
    server_version = "ESMTP Postfix (Debian/GNU)"
    # accepted data size; default = 33554432
    data_size = 33554432
