from socket import *
from urllib.parse import urlparse
import ssl
import sys

URI = sys.argv[1]
PORT = 80
is_supports_http2 = "no"
is_password_protected = "no"

# Parse uri string here
url_split = urlparse(URI)
if '/' in URI:
    HOST = url_split[1]
    PATH = url_split[2]
else:
    HOST = url_split[2]
    PATH = "/index.html"

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, 80))
request = f"GET {PATH} HTTP/1.1\n\n"
s.send(request.encode())
get_data = s.recv(10000)
s.close()
#print(get_data.decode())
get_message = get_data.decode().split('\n')

# Finds all cookies
cookies = []
for header in get_message:
    if 'Set-Cookie' in header:
        cookies.append(header)

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, 80))
request = f"OPTIONS / HTTP/1.1\r\n" 
request += f"Host: {HOST}\r\n"
request += "Connection: keep-alive\r\n"
request += "Upgrade: h2c\r\n"
request += "Accept: */*\r\n"
request += "\r\n"
s.send(request.encode())
data = s.recv(10000)
s.close()

response_headers = data.decode().split('\n')
status_line = response_headers[0].split(' ')
status_code = status_line[1]

if status_code == "200":
    is_supports_http2 = "yes"
else: # Second approach - if first approach fails
    context = ssl.create_default_context()
    context.set_alpn_protocols(['h2', 'http/1.1'])
    conn = context.wrap_socket(socket(AF_INET), server_hostname = HOST)
    conn.connect((HOST, 443))
    negotiated_protocol = conn.selected_alpn_protocol()
    if negotiated_protocol == 'h2':
        is_supports_http2 = "yes"

#Check if webpage is password-protected
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, 80))
ip = gethostbyname(HOST)
request = (
    f"GET {PATH} HTTP/1.1\r\n"
    f"Host: {ip}\r\n"
    "Connection: close\r\n"
    "\r\n"
)
s.send(request.encode())
data = s.recv(10000)
s.close()

response_header_pw = data.decode().split('\n')
pw_status = response_header_pw[0].split(' ')
status_num = pw_status[1]

if status_num == "401":
    is_password_protected = "yes"

print(f"website: {HOST}")
print(f"1. Supports http2: {is_supports_http2}")
print("2. List of Cookies:")
for cookie in cookies:
    print_cookie = ""
    cookie_properties = cookie.split(';')
    cookie_name = 'cookie: '
    temp = cookie_properties[0].split(' ')
    cookie_name += temp[1]
    print_cookie += cookie_name + ", "

    for property in cookie_properties:
        if 'expires' in property:
            cookie_expires = "expires time: "
            temp = property.split("=")
            cookie_expires += temp[1]
            print_cookie += cookie_expires + "; "

        if 'domain' in property:
            cookie_domain = "domain name: www"
            temp = property.split("=")
            cookie_domain += temp[1]
            temp = cookie_domain.split(';')
            final_cookie_domain = temp[0]
            print_cookie += final_cookie_domain
    
    print(print_cookie)

print(f"3. Password-protected: {is_password_protected}")