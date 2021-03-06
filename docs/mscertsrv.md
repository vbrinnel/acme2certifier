# CA handler for Microsoft Certification Authority Web Enrollment Service

This CA handler uses Microsofts [certsrv](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh831649) for certificate enrollment 
and the python library [magnuswatn](https://github.com/magnuswatn/)/[certsrv](https://github.com/magnuswatn/certsrv) for communication with the enrollment service.

When using the handler please be aware of the following limitations:

- Authentication towards Web Enrollment Service is limited to "basic" or "ntlm". There is currently no support for ClientAuth
- Communication is limited to https 
- Revocation operations are not supported

## Preparation
1. Microsoft Certification Authority Web Enrollment Service must be enabled and configured - of course :-)
2. You need to have a set of credentails with permissions to access the service and enrollment templates
3. Authentication method )basic or ntlm) to the service must be defined.

It is helpful to verify the service access before starting the configuration of acme2certifier
- service access by using ntlm authentication towards certsrv
```
root@rlh:~# curl -I --ntlm --user <user>:<password> -k https://<host>/certsrv/
```
- service access by using basic authentication
```
root@rlh:~# curl -I --user <user>:<password> -k https://<host>/certsrv/
```

Access to the service is possible if you see the status code 200 returned as part of the reponse
```
HTTP/1.1 200 OK
Cache-Control: private
Content-Length: 3686
Content-Type: text/html
Server: Microsoft-IIS/10.0
Set-Cookie: - removed - ; secure; path=/
X-Powered-By: ASP.NET
```

## Installation

- install [certsrv](https://github.com/magnuswatn/certsrv) via pip
```
root@rlh:~# pip install certsrv[ntlm]
```
- copy the ca_handler into the acme directory
```
root@rlh:~# cp example/mscertsrv_ca_handler.py acme/ca_handler.py
```
- modify the server configuration (/acme/acme_srv.cfg) and add the following parameters
```
[CAhandler]
host: <hostname>
user: <username>
password: <password>
ca_bundle: <filename>
auth_method: <basic|ntlm>
template: <name>
```
    - host - hostname of the system providing the Web enrollment service
    - user - username used to access the service
    - password - password
    - ca_bundle - CA certificate bundle in pem format needed to valiate the server certificate
    - auth_method - authentication method (either "basic" or "ntlm")
    - template - certificate template used for enrollment
    