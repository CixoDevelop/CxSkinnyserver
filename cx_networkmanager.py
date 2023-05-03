from cx_skinnyserver import urlparser
import network

class networkmanager:
    """
    This class is responsible for the network manager. It allows you to connect
    to a WiFi network, manage connections, configure the connection using the
    existing REST API.
    """
    
    
    def set_config(self, path, response):
        """
        This function modifies the configuration of a network device. It is an
        endpoint for a REST API and operates on data sent through URL
        arguments.
        :path: Path received from client
        :response: Response to client
        """
        
        options = urlparser.decode(path)
        config = self.__read_config()
        
        config.update(options)
        
        self.__save_config(config)
        self.__update_state()
    
    
    def get_config(self, path, response):
        """
        This function returns the current configuration of the device using URL
        encoding.
        :path: Path received from client
        :response: Response to client
        """
        
        response.headers["Content-Type"] = "application/x-www-form-urlencoded"
        response.body = urlparser.encode(self.__read_config())
    
    
    def __save_config(self, config):
        """
        This function saves the requested network configuration to the
        appropriate file.
        :config: Config dict to save
        """
        
        with open(self.config, "w") as file:
            file.write(self.__serialize_config(config))
    
    
    def __read_config(self):
        """
        It reads the configuration file, parses it, and returns it as a
        dictionary.
        :return: Prepared dict with configuration
        """
        
        try:
            with open(self.config) as file:
                return self.__parse_config(file.read())
        except:
            return dict()
        
    
    def __serialize_config(self, config):
        """
        It serializes the configuration by taking a dictionary and then
        translating it into a string in the INI format.
        :config: Config in dict
        :return: Serialized config
        """
        
        serialized = ""
        
        for key in config:
            serialized += key + "=" + config[key] + "\n"
        
        return serialized
    
    
    def __parse_config(self, config):
        """
        This function parses the read configuration in string format into a
        dictionary format, which it then returns.
        :config: Config in string format
        :return: Config in dict format
        """
        
        parsed = dict()
        
        for line in config.split("\n"):
            if not line:
                continue
            
            keys = line.split("=")
            parsed[keys[0]] = keys[1] if len(keys) else ""
        
        return parsed
    
    
    def __load_defaults(self):
        """
        This function loads the default network device configuration and then
        saves it.
        :return: Default config in dict format
        """
        
        config = {
            "hostname": "Cx_IoT_device",
            "sta-ssid": "",
            "sta-psk": "",
            "ap-ssid": "Config_Cx_IoT_device",
            "ap-psk": ""
        }
        
        self.__save_config(config)
        return config
        
        
    def __update_state(self):
        """
        This function reads the saved configuration from a file, and then sets
        the specified network configuration. If it can connect to an Access
        Point, it will maintain that connection, but if it cannot, it will
        create its own network according to the settings in the configuration
        file.
        """
        
        config = self.__read_config()
        ap = network.WLAN(network.AP_IF)
        sta = network.WLAN(network.STA_IF)
        
        if not config:
            config = self.__load_defaults()
        
        ap.active(False)
        sta.active(True)
        sta.config(dhcp_hostname = config["hostname"])
        sta.connect(config["sta-ssid"], config["sta-psk"])
        
        while sta.status() == network.STAT_CONNECTING:
            continue
        
        if sta.status() == network.STAT_GOT_IP:
            return
        
        sta.active(False)
        ap = network.WLAN(network.AP_IF)
        
        ap.config(essid = config["ap-ssid"])
        
        if config["ap-psk"]:
            ap.config(authmode = network.AUTH_WPA2_PSK)
            ap.config(password = config["ap-psk"])
        else:
            ap.config(authmode = network.AUTH_OPEN)
        
        ap.active(True)
        
    
    def __init__(self, server, config):
        """
        This function creates a new network manager. It requires specifying a
        REST server to add the endpoints required for configuring and reading
        network configuration.
        :server: REST server to add endpoints
        :config: Config file name 
        """
        
        self.server = server
        self.config = config
        
        self.server.add_path(self.get_config, "/network", "GET")
        self.server.add_path(self.set_config, "/network", "POST")
        
        self.__update_state()