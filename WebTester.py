from socket import *
from urllib.parse import urlparse
import ssl
import sys

HTTP_PORT = 80
HTTPS_PORT = 443

def getHost(uri):
    """
    Error check and get host and path address

    Returns:
        host: The host address
        path: The path of the URL
    """
    url_split = urlparse(uri)

    if '/ ' in uri:
        host = url_split[1]
        path = url_split[2]
    elif 'https' in uri:
        host = url_split[1]
        path = url_split[2]
    else:
        host = url_split[2]
        path = "/index.html"

    try:
        proper_host_name = gethostbyname(host)
    except gaierror as e:
        print(f"Error: Invalid hostname {uri} ")
        exit(1)
    
    return (host, path)

def getCookies(host, path):
    """
    Finds cookies by using an HTTP protocol

    Args:
        host: The host address 
        path: The path of the URL
    
    Returns:
        response: HTTP message headers
        cookies: String of cookie information
    """
    cookies = []

    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, HTTP_PORT))
        request = f"GET {path} HTTP/1.1\n\n"
        s.send(request.encode())
        get_data = s.recv(10000)
        s.close()
    except ConnectionRefusedError as e:
        print(f"Error: Invalid hostname {host} ")
        exit(1)
        

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, HTTP_PORT))
    request = f"OPTIONS / HTTP/1.1\r\n" 
    request += f"Host: {host}\r\n"
    request += "Connection: keep-alive\r\n"
    request += "Upgrade: h2c\r\n"
    request += "Accept: */*\r\n"
    request += "\r\n"
    s.send(request.encode())
    data = s.recv(10000)
    response = data.decode()
    s.close()

    get_message = get_data.decode().split('\n')
    for header in get_message:
        if 'Set-Cookie' in header and header not in cookies:
            cookies.append(header)

    if '302' not in response or '301' not in response:
        try:
            context = ssl.create_default_context()
            conn = context.wrap_socket(socket(AF_INET), server_hostname = host)
            conn.connect((host, HTTPS_PORT))
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            conn.send(request.encode())
            get_data = conn.recv(1024)
            response = get_data.decode()
        except ssl.SSLCertVerificationError as e:
            print(f'SSL Verification Failed - Invalid Host name: {host}')
            exit(1)
        except ssl.SSLError as e:
            print("SSL Error occurred")
            exit(1)

        while '302' in response or '301' in response:
            temp = response.split('\n')
            new_host = temp[1].split(': ')[1]
            host, path = getHost(new_host)

            if 'https' in new_host:
                try:
                    context = ssl.create_default_context()
                    conn = context.wrap_socket(socket(AF_INET), server_hostname = host)
                    conn.connect((host, HTTPS_PORT))
                    request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                    conn.send(request.encode())
                    get_data = conn.recv(1024)
                    response = get_data.decode()
                except ssl.SSLCertVerificationError as e:
                    print(f'SSL Verification Failed - Invalid Host name: {host}')
                    exit(1)
                except ssl.SSLError as e:
                    print("SSL Error occurred")
                    exit(1)
        
        get_message = get_data.decode().split('\n')
        for header in get_message:
            if 'Set-Cookie' in header and header not in cookies:
                cookies.append(header)

    while '302' in response or '301' in response:
        temp = response.split('\n')
        new_host = temp[1].split(': ')[1]
        host, path = getHost(new_host)

        if 'https' in new_host:
            try:
                context = ssl.create_default_context()
                conn = context.wrap_socket(socket(AF_INET), server_hostname = host)
                conn.connect((host, HTTPS_PORT))
                request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                conn.send(request.encode())
                get_data = conn.recv(1024)
                response = get_data.decode()
            except ssl.SSLCertVerificationError as e:
                print(f'SSL Verification Failed - Invalid Host name: {host}')
                exit(1)
            except ssl.SSLError as e:
                print("SSL Error occurred")
                exit(1)

    get_message = get_data.decode().split('\n')
    for header in get_message:
        if 'Set-Cookie' in header and header not in cookies:
            cookies.append(header)

    return (response, cookies)

def getHTTP2Status(host, response):
    """
    Check and print out the http2 compatibility

    Args:
        host: The host address
        response: HTTP message headers

    Returns:
        is_supports_http2: A string of either "yes" or "no" depending
                           on if the webpage supports http2
    """
    is_supports_http2 = "no"
    response_headers = response.split('\n')
    status_line = response_headers[0].split(' ')
    status_code = status_line[1]
    try:
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2', 'http/1.1'])
        conn = context.wrap_socket(socket(AF_INET), server_hostname = host)
        conn.connect((host, HTTPS_PORT))
        negotiated_protocol = conn.selected_alpn_protocol()
    except ssl.SSLCertVerificationError as e:
        print(f'SSL Verification Failed - Invalid Host name: {host}')
        exit(1)
    except ssl.SSLError as e:
        print("SSL Error occurred")
        exit(1)

    if 'HTTP2-Settings' in response_headers:
        is_supports_http2 = "yes"

    if negotiated_protocol == 'h2':
        is_supports_http2 = "yes"

    conn.close()
    return is_supports_http2

def getPasswordProtectedStatus(host, path, response):
    """
    Checks and outputs if the webpage is password protected

    Args:
        host: The host address
        path: The path of the URL
        response: HTTP message headers

    Returns:
        is_password_protected: Outputs "yes" or "no" depending on whether the
                               webpage is password-protected
    """
    is_password_protected = "no"

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((host, HTTP_PORT))
    ip = gethostbyname(host)
    request = (
        f"GET {path} HTTP/1.1\r\n"
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

    return is_password_protected

def printHTTPInfo(host, response, cookies, http2_status, password_protected_status):
    """
    Prints out webpage HTTP protocol information

    Args:
        host: The host address
        response: HTTP message headers
        cookies: String of cookie information
        http2_status: A string of either "yes" or "no" depending
                      on if the webpage supports http2
        password_protected_status: A string of either "yes" or "no" depending on whether the
                                   webpage is password-protected
    """
    print(f"website: {host}")
    print(f"1. Supports http2: {http2_status}")
    print("2. List of Cookies:")
    for cookie in cookies:
        print_cookie = ""
        cookie_properties = cookie.split(';')
        cookie_name = 'cookie: '
        temp = cookie_properties[0].split(' ')
        temp2 = temp[1].split('=')
        cookie_name += temp2[0]
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
    
        print(f"{print_cookie}")

    print(f"3. Password-protected: {password_protected_status}")

def main():

    try:
        uri = sys.argv[1]
    except IndexError as e:
        print(f"Error: Hostname does not exist")
        exit(1)
        
    #get and check url
    host, path = getHost(uri)
    
    #get cookies
    response, cookies = getCookies(host, path)
    
    #check and get http/2 status
    http2_status = getHTTP2Status(host, response)
    
    #check and get password-protection status
    password_protected_status = getPasswordProtectedStatus(host, path, response)

    #print HTTP webpage information
    printHTTPInfo(host, response, cookies, http2_status, password_protected_status)

if __name__ == "__main__":
    main()