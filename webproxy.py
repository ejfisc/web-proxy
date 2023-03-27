# Web Proxy
# CS 4390.002 - Computer Networks - S23 
# Due: May 01, 2023
# Python 3.11.1
# References:
# # COMPUTER NETWORKING: A Top-Down Approach 
# # # Section 2.7.2 Socket Programming with TCP
# # # Section 2.2.3 HTTP Message Format
# I am using 4096 bytes because 1024 is not big enough which causes cut-offs

from socket import *

# Create a server socket welcomeSocket, bind to a port p # This is the welcoming socket used to listen to requests coming from a client
# Listen on welcomeSocket
serverPort = 5005
welcomeSocket = socket(AF_INET,SOCK_STREAM)
welcomeSocket.bind(("",serverPort))
welcomeSocket.listen(1)

# Virtual cache
cache = dict()
useCases = ["gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file4.html",
            "www.google.com/unknown",
            "www.google.com",
            "www.utdallas.edu/~kvl140030/4390/Earth.jpg"]

while True:
    # print ‘WEB PROXY SERVER IS LISTENING’
    print("WEB PROXY SERVER IS LISTENING\n")

    # Wait on welcomeSocket to accept a client connection
    # When a connection is accepted, a new client connection socket is created. Call that socket clientSocket
    # Read the client request from clientSocket
    clientSocket, addr = welcomeSocket.accept()
    message = clientSocket.recv(4096).decode()

    # Process the request
    # Split the message to extract the header
    # Parse the header to extract the method, dest address, HTTP version
    splitMsg = message.split()
    method = splitMsg[0]
    destAddr = splitMsg[1].removeprefix("/") # Removes the preceding "/"
    httpVer = splitMsg[2]

    # Focus on use cases and ignore the favicon browser request spam
    if destAddr not in useCases:
        continue

    # Print the message received from the client
    # This is slightly out of order to prevent favicon browser request spam
    print("*** MESSAGE RECEIVED FROM CLIENT")
    print(message + "\n")
    
    # Print the extracted method, dest address and HTTP version
    print("*** [PARSE MESSAGE HEADER]:")
    print(" METHOD = " + method + ", DESTADDRESS = " + destAddr + ", HTTPVersion = " + httpVer + "\n")


    # if method is GET
    if (method == "GET"):

        # Look up the cache to determine if requested object is in the cache
        # if object is not in the cache need to request object from the original server
        if destAddr not in cache.keys():
            # Print “Object not found in the cache” message
            print("*** [LOOK UP IN THE CACHE]: NOT FOUND, BUILD REQUEST TO SEND TO ORIGINAL SERVER")
            host = destAddr.partition("/")[0] # If the separator is not found, return a 3-tuple containing the string itself, followed by two empty strings.
            url = destAddr.partition("/")[2]
            fileName = destAddr.rpartition("/")[2]
            print("[PARSE REQUEST HEADER] HOSTNAME IS " + host)
            if (url != ""):
                print("[PARSE REQUEST HEADER] URL IS " + url)
            # Include the fileName ! = host because rpartition will fill from right to left, thus if the separator is not in the string
            # the last element in the tuple becomes filled with the entire string and the other two elements are blank.
            # The entire string in this case will be the hostname.
            if (fileName != "" and fileName != host):
                print("[PARSE REQUEST HEADER] FILENAME IS " + fileName)
            print()

            # Create a serverSocket to send request to the original server
            # Compose the request header, send request
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.connect((host, 80))
            # Remember the line ends with a carraige return and a line feed
            requestHeader = ("GET /{path} {httpV}\r\n".format(path = url, httpV = httpVer) +
            "Host: {hostName}\r\n".format(hostName = host) +
            "Connection: close\r\n" +
            "User-Agent: python-script/3.11.1\r\n" +
            "Accept-language: en\r\n" +
            "\r\n")
            serverSocket.send(requestHeader.encode())

            # Print the request sent to the original server
            print("*** REQUEST SENT TO THE ORIGINAL SERVER")
            print(requestHeader)

            # Read response from the original server
            # Parse it to extract the relevant components
            response = serverSocket.recv(4096).decode()
            responseHeader = response.partition("\r\n\r\n")[0]

            # Print the response header from the original server
            print("*** RESPONSE HEADER FROM THE ORIGINAL SERVER")
            print(responseHeader)

            # if response is 200 OK
            # Write object into cache
            statusCode = responseHeader.split()[1]
            if (statusCode == "200"):
                cache[destAddr] = response
            
            # Close serverSocket
            serverSocket.close()

            # Compose response and send to client on clientSocket
            clientSocket.send(response.encode())

            # Print the response header from the proxy to the client
            print("\n*** RESPONSE FROM PROXY TO CLIENT")
            cachedResponseHeader = cache[destAddr].partition("\r\n\r\n")[0]
            print(cachedResponseHeader + "\n")
    
        # if object is in the cache
        else:
            # Print “Object found in the cache” message
            print("*** [LOOK UP THE CACHE]: FOUND IN THE CACHE: FILE =" + destAddr)

            # Read from the cache, compose response, send to client on clientSocket
            clientSocket.send(cache[destAddr].encode())

            # Print the response header from the proxy to the client
            print("\n*** RESPONSE FROM PROXY TO CLIENT")
            cachedResponseHeaderFound = cache[destAddr].partition("\r\n\r\n")[0]
            print(cachedResponseHeaderFound + "\n")

    # Method is not GET
    else:
        print("METHOD IS NOT A GET")

    # Close clientSocket
    # End of while True
    clientSocket.close()

# Close welcomeSocket
welcomeSocket.close()