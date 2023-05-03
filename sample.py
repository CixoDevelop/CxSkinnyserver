import cx_skinnyserver
import socket

# Create socket
sample_socket = socket.socket()
sample_socket.bind(("0.0.0.0", 8080))

# Create services
def hello_world(path, response):
    response.body = "Hello World!"
    response.headers["Content-Type"] = "text/html"

def sample_decoder(path, response):
    response.body = str(cx_skinnyserver.urlparser.decode(path))

def sample_encoder(path, response):
    response.body = cx_skinnyserver.urlparser.encode({"Test": "content"})

# Create server
sample_server = cx_skinnyserver.server(sample_socket)

# Bind services
sample_server.add_path(hello_world, "/", "GET")
sample_server.add_path(sample_decoder, "/decoder", "GET")
sample_server.add_path(sample_encoder, "/encoder", "GET")

# Start listening
sample_server.listen()
