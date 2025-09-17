from socket import *
import ssl
import sys

URI = sys.argv[1]
PORT = 80
is_supports_http2 = "no"
is_password_protected = None
# Parse uri string here
# Use uri.split("/") or/and uri.split(".")
    
s = socket(AF_INET, SOCK_STREAM)

s.connect((URI, 80))
s.send("GET /index.html HTTP/1.0\n\n")
get_data = s.recv(10000)
s.close()
print(get_data)
get_message = get_data.split('\n')

# Finds all cookies
cookies = []
for header in get_message:
    if 'Set-Cookie' in header:
        cookies.append(header)

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

if status_code == "200":
    is_supports_http2 = "yes"
else: # Second approach - if first approach fails
    context = ssl.create_default_context()
    context.set_alpn_protocols(['h2', 'http/1.1'])
    conn = context.wrap_socket(socket(AF_INET), server_hostname = URI)
    conn.connect((URI, 443))
    negotiated_protocol = conn.selected_alpn_protocol()
    if negotiated_protocol == 'h2':
        is_supports_http2 = "yes"


print("website: %s" % URI)
print("1. Supports http2: %s" % is_supports_http2)
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

print("3. Password-protected: %s" % is_password_protected)