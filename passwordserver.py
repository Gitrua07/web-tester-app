from http.server import HTTPServer, SimpleHTTPRequestHandler
import base64

class BasicAuthHandler(SimpleHTTPRequestHandler):
    def do_HEAD(self):
        if not self.headers.get('Authorization'):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Protected"')
            self.end_headers()
            return
        auth_type, credentials = self.headers.get('Authorization').split()
        user_pass = base64.b64decode(credentials).decode('utf-8')
        username, password = user_pass.split(':')
        if username == "admin" and password == "password":
            return super().do_HEAD()
        else:
            self.send_response(401)
            self.end_headers()

    def do_GET(self):
        self.do_HEAD()
        return super().do_GET()

server_address = ('', 8000)
httpd = HTTPServer(server_address, BasicAuthHandler)
print("Serving on port 8000 with basic auth (username: admin, password: password)")
httpd.serve_forever()
