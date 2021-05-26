# service_socket_wrapper
A simple Python wrapper around a service that you communicate with over TCP. Makes it easier to send commands and read the output.

The tricky part of this program was making sure to read all of the information returned by the service after each command. Sometimes there is just one terminal response, but sometimes there are one or more non-terminal responses before the final terminal response.
