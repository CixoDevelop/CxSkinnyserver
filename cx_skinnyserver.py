import gc

class urlparser:
    """
    This class store static functions, thats are responsible for encoding and
    decoding dicts with data from and to strings, that can be received from
    path from client, or send by response body.
    """
    
    
    @staticmethod
    def encode(structure):
        """
        This function encode dict structure to URL-encoded string format.
        :structure: Dict structure
        :return: Same structure as string
        """
        
        encoded = "?"

        for key in structure:
            encoded += __class__.__encode_string(key) + "="
            encoded += __class__.__encode_string(str(structure[key])) + "&"

        return encoded[:-1]


    @staticmethod
    def decode(url):
        """
        This function decode arguments given in string format, and return
        decoded dict.
        :url: URL string to decode
        :return: Decoded dict
        """
        
        structure = dict()

        if url.find("?") != -1:
            url = url[url.find("?") + 1:]

        for part in url.split("&"):
            try:
                splited = part.split("=")
                key = __class__.__decode_string(splited[0])
                value = __class__.__decode_string(splited[1])
                
                structure[key] = value

            except:
                continue

        return structure
    
    
    @staticmethod
    def __decode_string(content):
        """
        This decode special characters from url (%ff) to standard python
        string.
        :content: Content to decode
        :return: Decoded string
        """
        
        result = bytes()
        content = list(content)
        while len(content):
            char = content.pop(0)
            if char != "%":
                result += bytes(char, 'UTF-8')
                continue
            
            char = content.pop(0)
            char += content.pop(0)
            result += bytes([int(char, 16)])
            
        return result.decode("UTF-8")
    
    
    @staticmethod
    def __encode_string(content):
        """
        This encode content, from normal python string to (%ff) http path form.
        :content: Normal python string to encode
        :return: Encoded string
        """
        
        return "".join([__class__.__encode_char(char) for char in content])
    
    
    @staticmethod
    def __encode_char(char):
        """
        This function encode single char to url encoded.
        :char: Char to encode
        :return: Encoded char
        """
        
        if char.isalpha() or char.isdigit():
            return char
        
        return str(char.encode("UTF-8"))[2:-1].replace("\\x", "%").upper()


class server_response:
    """
    This class is a response from the server for cx_skinnyserver. It stores
    headers, response status, and content. This class also generates the string
    to be returned to the user.
    """
    
    
    def __init__(self):
        """
        This function creates a new instance of a response. By default, it
        closes the connection and sets the response status to be successful.
        :return: New response object
        """
        
        self.mark_ok()
        self.headers = {
            "Connection": "close",
        }
        self.body = ""


    def mark_ok(self):
        """
        This function mark response as OK.
        """
        
        self.status_code = 200
        self.status_text = "OK"
        self.body = "OK"


    def mark_internal_error(self):
        """
        This function mark response as Internal Server Error.
        """
        
        self.status_code = 500
        self.status_text = "Internal Server Error"
        self.body = "Internal Server Error"


    def mark_not_found(self):
        """
        This function mark response as Not Found.
        """
        
        self.status_code = 404
        self.status_text = "Not Found"
        self.body = "Not Found"


    def mark_bad_request(self):
        """
        This function mark response as Bad Request.
        """
        
        self.status_code = 400
        self.status_text = "Bad Request"
        self.body = "Bad Request"


    def serialize(self):
        """
        This function serialize response, and return string ready to send to
        client socket.
        :return: Serialized response
        """
        
        serialized = "HTTP/1.1 " + str(self.status_code) + " "
        serialized += self.status_text + "\r\n"
        
        self.headers["Content-Length"] = len(self.body)

        for header in self.headers:
            serialized += header + ": " + str(self.headers[header]) + "\r\n"

        serialized += "\r\n" + self.body

        return serialized


class server:
    """
    This class is responsible for an instance of the cx_skinnyserver server.
    It is responsible for a single instance listening on a single port.
    """
    
    
    def __init__(self, socket):
        """
        This function creates a REST server on the specified socket. The
        server is empty, with no endpoints
        :socket: Socket to listen on
        :return: New server instance
        """
        
        self.socket = socket
        self.pathes = dict()
        self.listening = False
        
        
    def close(self):
        """
        This function closing server (server exit from listening loop, after
        run this function from service).
        """
        
        self.listening = False
        
        
    def add_path(self, callback, path = "/", method = "GET"):
        """
        This function binds a new service to the server. Adding it requires
        specifying the path, method, and callback (service). A service is a
        function that takes the path and response as arguments. The path is the
        path the user came in on, and we can extract data passed in through
        URL-encoded methods. The response is a cx_response object that will be
        serialized and sent back to the client.
        :callback: Service to run when client go to specified path
        :path: Path to bind service
        :method: Method to bind service
        """
        
        self.pathes[method + path] = callback


    def listen(self):
        """
        This function is the server listening loop. When this function is
        called, the server's listening loop is started. The server will exit
        this loop only when the close() function is called on the server
        object.
        """
        
        self.socket.listen(10)
        self.listening = True

        while self.listening:
            gc.collect()
            
            client, address = self.socket.accept()
            request = client.makefile("rwb", 0).readline()
            
            if isinstance(request, bytes):
                request = request.decode("UTF-8")
            
            request = request.split(" ")
            response = server_response()
            method = request[0]
            path = request[1]
            
            if path.find("?") == -1:
                clean_path = path
            else:
                clean_path = path[:path.find("?")]

            if method + clean_path not in self.pathes:
                response.mark_not_found()
                client.sendall(response.serialize().encode("UTF-8"))
                continue

            try:
                self.pathes[method + clean_path](path, response)
            except:
                response.mark_internal_error()
            
            client.sendall(response.serialize().encode("UTF-8"))

                
