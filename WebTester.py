from socket import *
import ssl
import sys

URI = sys.argv[1]
PORT = 80
is_supports_http2 = None
is_password_protected = None
# Parse uri string here
# Use uri.split("/") or/and uri.split(".")
    
s = socket(AF_INET, SOCK_STREAM)
s.connect((URI, 80))
request = "OPTIONS / HTTP/1.1\r\n" 
request += "Host: {}\r\n".format(URI)
request += "Connection: keep-alive\r\n"
request += "Upgrade: h2c\r\n"
request += "Accept: */*\r\n"
request += "\r\n"
s.send(request)
data = s.recv(10000)
s.close()

response_headers = data.split('\n')
status_line = response_headers[0].split(' ')
status_code = status_line[1]

if status_code != "302" and status_code != "405":
    pass #then check if h2 line exists
else: # Second approach - if first approach fails
    context = ssl.create_default_context()
    context.set_alpn_protocols(['h2', 'http/1.1'])
    conn = context.wrap_socket(socket(AF_INET), server_hostname = URI)
    conn.connect((URI, 443))
    negotiated_protocol = conn.selected_alpn_protocol()
    if negotiated_protocol == 'h2':
        is_supports_http2 = 'yes'
    else:
        is_supports_http2 = 'no'


print("website: %s" % URI)
print("1. Supports http2: %s" % is_supports_http2)
print("2. List of Cookies:")
for cookie in range(1, 3):
    print("cookie: <cookie name %d>, expires time: ..; domain name: <domain name %d>" % (cookie, cookie))
print("3. Password-protected: %s" % is_password_protected)