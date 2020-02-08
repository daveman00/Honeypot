
class SSHServerSettings:
    # address of the server; present binds to all interface
    bind_address = "0.0.0.0"
    # port of the SSHService service
    server_port = 22
    # the SSHService server version
    server_version = "OpenSSH_7.6p1 Debian-2"
    # connection timeout setting
    timeout = 10
    # rsa private key location
    private_rsa = "Honeypot/Services/SSHService/test_rsa.key"
