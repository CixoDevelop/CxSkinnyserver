# CxSkinnyServera


## What is this?

This project is a lightweight and stripped-down REST server providing maximum 
performance, even on the ESP8266. It allows for communication with IoT 
devices through a web browser application, which is not possible with standard 
network sockets. However, if you plan on sending a lot of information, such as 
files that cannot fit in the server's path parameters, then unfortunately this 
is not the solution for you. Currently, to maximize server performance, the 
server simply processes the first line of the user's request header and then 
calls the service bound to that path, passing the entire received path with 
its parameters and the response that should be modified by the service as a 
parameter. This response will then be sent back to the client. The service can 
perform various actions based on its arguments, control GPIO pins, send data 
via UART, and so on. It can also read files from Flash memory and send them as 
a response. Additionally, the project provides a network manager that is 
compatible with the REST server. It allows for the saving and modification of 
network configurations through requests to the server. The server itself is 
compatible with the standard implementation of Python 3, although there are 
obviously much better solutions for computers, such as Django or FastAPI. 
Unfortunately, the network manager is not compatible with standard Python 3 
for obvious reasons.


## How to create simple project?

You should start by uploading the cx_skinnyserver.py file and (if you want to 
use the network manager) cx_networkmanager.py file. Then, you need to import 
cx_skinnyserver, for example by using the 
```
import cx_skinnyserver
```
statement.
You also need to import sockets since the server requires a socket bound to 
an address to listen on. For sample
```
import socket
sample_socket = socket.socket()
sample_socket.bind(("0.0.0.0", 80))
```
Now you can proceed with creating an instance of the server.
```
server = cx_skinnyserver.server(sample_socket)
```
And we will create a very simple service that returns 'Hello World!' when 
called.
```
def hello_world(path, response):
    response.body = "Hello World!"
    response.headers["Content-Type"] = "text/html"
```
And finally, we just need to bind the service to the server and start its 
main loop.
```
server.add_path(hello_world, "/", "GET")
server.listen()
```
Such a simple example code is available in the sample.py file. This file also 
includes examples of using objects for encoding and decoding path parameters. 
Thanks to this, we can use data sent by path parameters as ordinary Python 
dictionaries and send Python dictionaries as strings.


## How to use URLparser?

The URLparser is a component of the cx_skinnyserver project. MicroPython does 
not have native support for this method of data encoding, so there was a need 
to write a custom implementation. The entire implementation has been composed 
into a static class, which has two functions. One encodes Python dictionaries 
into URLencoded format, while the other decodes URLencoded data into Python 
dictionary format. So, to encode a dictionary, you need to
```
encoded_data = cx_skinnyserver.urlparser.encode({"key": "value"})
```
To decode the path, you need to
```
decoded_dict = cx_skinnyserver.urlparser.decode("?key=value&key2=value2")
```
Data to decode can be passed from path param in service.


## How to use network manager?

Start by importing the cx_networkmanager.py file, then create the server as 
described above. The network manager uses configuration from an ini file, but 
also allows for changing the configuration using an endpoint on the server. 
Once we have created the server, we call the following instructions
```
manager = cx_networkmanager.networkmanager(rest_server, "network_config.ini")
```
The network manager parses the configuration, then tries to establish a 
connection, and if it fails or the configuration for the access point to which 
it can connect does not exist, the manager creates its own access point 
according to the configuration, or if the configuration is empty, according to 
the default configuration. By adding an endpoint to the REST API, you can 
manage the network using HTTP requests from another device. The available 
options are
```
GET /network - Return current configuration as URLencoded data
POST /network - Change options set in path arguments. Avairable options are
 * hostname - Device hostname
 * sta-ssid - SSID of station, which device try to connect
 * sta-psk - Password to station, empty when station is open
 * ap-ssid - SSID of access point, that device create when cannot connect 
 * ap-psk - Password for access point, that device create, empty when open
For example:
POST /network?hostname=Device&sta-ssid=SSID - Change hostname and sta-ssid
```

## Nice job!
