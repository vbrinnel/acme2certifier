# Support for an Openssl based CA stored on local file system
The openssl CA handler is rather for testing and lab usage. I strongly recommend not to reuse it in production environments without reviewing local system configuration and hardening state

## Prerequisites
You need to create a certificate authority on the local file-system.

I did it by running the below command:
```
root@rlh:~# openssl req -x509 -new -extensions v3_ca -newkey rsa:4096 -keyout ca-key.pem -out ca-cert.pem -days 3650
```

## Configuration
 - copy the ca_handler into the acme directory
```
root@rlh:~# cp example/ca_handlers/openssl_ca_handler.py acme/ca_handler.py
```
 - create a directory to store the (ca) certificate(s), key and CRL(s)
```
root@rlh:~# mkdir acme/ca
root@rlh:~# mkdir acme/ca/certs
```
 - place the above generated key and cert into the "ca" directory
```
root@rlh:~# mv ca-key.pem acme/ca/
root@rlh:~# mv ca-cert.pem acme/ca/
```

 - modify the server configuration (/acme/acme_srv.cfg) and add the following parameters
```
[CAhandler]
issuing_ca_key: acme/ca/ca-key.pem
issuing_ca_key_passphrase: Test1234
issuing_ca_cert: acme/ca/ca-cert.pem
issuing_ca_crl: acme/ca/crl.pem
cert_validity_days: 30
cert_save_path: acme/ca/certs
ca_cert_chain_list: []
```
    - issuing_ca_key - private key of the issuing CA (in PEM format) used to sign certificates and CRLs
    - issuing_ca_key_passphrase - password to access the private key
    - issuing_ca_cert - Certificate of issuing CA in PEM format
    - issuing_ca_crl - CRL of issuing CA in PEM format
    - cert_validity_days - certificate lifetime in days (default 365)
    - cert_save_path - directory to store then enrolled certificates (optional)
    - ca_cert_chain_list - List of root and intermediate CA certificates to be added to the bundle return to an ACME-client (the issueing CA cert must not be included)

 - enjoy enrolling and revoking certificates

some remarks:
 - certificates and CRls will be signed with sha256
 - during enrollment all extensions included in the csr will be copied to the certificate. Don’t tell me that this is a bad idea. Read the first two sentences of this page instead.
 - if not available in csr the following extensions will be added to a certificate
    - authorityKeyIdentifier: False
    - keyid: always
    - extendedKeyUsage: False
    - clientAuth
 - the CRL "next update interval" is 7days
