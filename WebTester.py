from socket import *
import sys

uri = sys.argv[1]

# Parse uri string here
# Use uri.split("/") or/and uri.split(".")

s = socket(AF_INET, SOCK_STREAM)
s.connect(("www.google.ca", 80))
s.send("GET/index.html HTTP/1.0\n\n")
data = s.recv(10000)
s.close()