import socket
import os

ROOT_DIRECTORY = "./data"
CURRENT_DIRECTORY = "./data"

# generates html to show the directory contents
def add_filelist_in_html(content: str, dirpath: str) -> str:

    lst = ""
    teststr = ROOT_DIRECTORY
    if( CURRENT_DIRECTORY.endswith("/")):
        teststr +='/'
 
    lst += 'Current Folder :'
    lst += CURRENT_DIRECTORY
    lst += '<br>'
    if( teststr != CURRENT_DIRECTORY) :
        lst += '<a href="/go_up">Go up one level</a>'

    clist = "<ul>"
    # for i in os.walk(dirpath):
    dircnt = os.listdir(dirpath)
    count = len(dircnt)
    for j in os.listdir(dirpath):
        typ = os.path.isdir(os.path.join(dirpath, j))
        if typ:
            clist += '<li style="width:40%" class="fa fa-folder" >'+'<a style="margin-left: 5px;" href="'+str(j)+'">  '+str(j)+'</a></li><br>'
        else:
            clist += '<li style="width:40%" class="fa fa-file-o" >'+'<a style="margin-left: 5px;" href="'+str(j)+'">  '+str(j)+'</a>'+ \
                        '<form action="/delete" method="post"  enctype="multipart/form-data" style="width:0px;float:right"><input hidden type="text" name="filename" value="'+ \
                            str(j)+'"/><button name="submit"><p style="margin:0px;float:right" class="fa fa-trash"></p></button></form></li><br>'
    clist += "</ul>"

    if( count > 0):
        lst +=clist
    else:
        lst +="<p><h4>No files in directory</h4></p>"
    
    content = content.replace("Ninad_file_here", lst)
    
    return content


# return the contents from the file path to be rendered on page
# if file path is a file, then it returns the contnet of file ( image/png/gif)
# if file path is directory, it returns the contents populated in index.html
def get_file_data(filepath: str, binary: bool) -> str:
    global CURRENT_DIRECTORY
    #print("Filepath: ", filepath)
    if filepath == "./":
        with open("index.html", "r") as f:
            data = f.read()
        data = add_filelist_in_html(data, "data/").encode()
        # CURRENT_DIRECTORY = filepath
    else:
        if binary:
            with open(filepath, "rb") as f:
                data = f.read()
        else:
            if os.path.isdir(filepath):
                CURRENT_DIRECTORY = filepath
                with open("index.html", "r") as f:
                    data = f.read()
                data = add_filelist_in_html(data, CURRENT_DIRECTORY).encode()
                if CURRENT_DIRECTORY[-1] == "/":
                    CURRENT_DIRECTORY = CURRENT_DIRECTORY[:-1]

            else:
                with open(filepath, "r") as f:
                    data = f.read().encode()
    return data


# method to handle GET request coming from browser
def handle_get_requests(client_socket: socket.socket, resource: str) -> None:
    global CURRENT_DIRECTORY
    
    #print(CURRENT_DIRECTORY + resource)
    header = "HTTP/1.1 "
    if resource == "/go_up":
        if ROOT_DIRECTORY == CURRENT_DIRECTORY :
            header += "302 OK \nLocation: /home \n" 
            header += "Content-Type: text/html\n\n"
            client_socket.send(header.encode()) 
        else:
            header += "200 OK\n"
            prev_level = CURRENT_DIRECTORY
            rev_level = prev_level[::-1]
            ind = len(CURRENT_DIRECTORY) - rev_level.index("/") - 1
            CURRENT_DIRECTORY = prev_level[:ind]
            #print("CURRENT_DIRECTORY", CURRENT_DIRECTORY)
            req_data = get_file_data(CURRENT_DIRECTORY, False)
            header += "Content-Type: text/html\n\n"
            client_socket.send(header.encode())
            client_socket.send(req_data)
    elif resource == "/home":
        CURRENT_DIRECTORY = ROOT_DIRECTORY
        header += "200 OK\n"
        header += "Content-Type: text/html\n\n"
        binary_bool = False
        #print( header)
        req_data = get_file_data(CURRENT_DIRECTORY, binary_bool)
        client_socket.send(header.encode())
         
        client_socket.send(req_data)
    elif resource.startswith('/static'):
        filetype = resource.split(".")[-1]
        binary_bool = False
        header += "200 OK\n"
        if filetype == "html":
            header += "Content-Type: text/html\n"
        elif filetype == "jpg" or filetype == "jpeg":
            header += "Content-Type: image/jpeg\n"
            binary_bool = True
        elif filetype == "png" :
            header += "Content-Type: image/png\n"
            binary_bool = True
        req_data = get_file_data('./'+resource, binary_bool)
        header += "\n"
        client_socket.send(header.encode())
         
        client_socket.send(req_data)
    elif os.path.exists(CURRENT_DIRECTORY + resource):
        filetype = resource.split(".")[-1]
        binary_bool = False
        header += "200 OK\n"
        if filetype == "html":
            header += "Content-Type: text/html\n"
        elif filetype == "jpg" or filetype == "jpeg":
            header += "Content-Type: image/jpeg\n"
            binary_bool = True
        elif filetype == "png" :
            header += "Content-Type: image/png\n"
            binary_bool = True
        elif filetype == "gif" or filetype == "webp":
            header += "Content-Type: image/avif\n"
            binary_bool = True
        elif filetype == "js":
            header += "Content-Type: text/javascript\n"
        elif filetype == "css":
            header += "Content-Type: text/css\n"
        else:
            header += "Content-Type: text/html\n"
        req_data = get_file_data(CURRENT_DIRECTORY + resource, binary_bool)
        header += "\n"
        client_socket.send(header.encode())
         
        client_socket.send(req_data)
    else:
        #print("Error 404 Not found")
        header = "HTTP/1.1 404 Not Found\n\n"
        client_socket.send(header.encode())
    client_socket.send("\n\n".encode())
    return


# method to handle POST request coming from browser
# 1. Upload of images into the folder
# 2. Creation of new folder

def handle_post_requests(client_socket: socket.socket, resource: str) -> None:
    global CURRENT_DIRECTORY
    #print("CURRENT_DIRECTORY in post:", CURRENT_DIRECTORY)

    header = "HTTP/1.1 "
    # filename = filename.split("&")[0]
    # filename = filename[8:]
    print(resource)
    if resource == '/upload':
        file_header = get_payload(client_socket)
        filename = file_header.decode().split(";")[2].split('"')[1]
        filename = CURRENT_DIRECTORY+"/"+filename

        file_data = get_payload(client_socket)
        # #print("Header:", file_header)
        print("Payload", file_data)
        if " " in filename:
            filename = filename.replace(" ", "_")
        with open(filename, "wb") as f:
            f.write(file_data)
        
        header += "200 OK\n"
        header += "Content-Type: text/html\n\n"
        client_socket.send(header.encode())
        client_socket.send("\n\n".encode())
        client_socket.send(get_file_data(CURRENT_DIRECTORY, False))

        #print("CURRENT_DIRECTORY after post:", CURRENT_DIRECTORY)
    elif resource == '/addfolder':

        file_header = get_payload(client_socket) 
        print(file_header)
        formdata = get_payload(client_socket)
        print(formdata)
        foldername = formdata.decode().split("\r\n")[0]
        foldername = CURRENT_DIRECTORY+'/'+foldername
        #print(foldername)
        if( os.path.exists(foldername) == False):
            os.mkdir(foldername)
            CURRENT_DIRECTORY = foldername

        print(CURRENT_DIRECTORY)
        header += "200 OK\n"
        header += "Content-Type: text/html\n\n"
        # print(header)
        client_socket.send(header.encode())
        data = get_file_data(CURRENT_DIRECTORY, False)
        # print(data)
        client_socket.send(get_file_data(CURRENT_DIRECTORY, False))

        print("Data sent to browser")

    elif "/delete" in resource:
        print("CURRENT_DIRECTORY delete", CURRENT_DIRECTORY)

        file_header = get_payload(client_socket)
        print(file_header)
        formdata = get_payload(client_socket)
        print(formdata)
        filename = formdata.decode().split("\r\n")[0]
        filename = CURRENT_DIRECTORY+"/"+filename

        os.remove( filename)

        print(CURRENT_DIRECTORY)
        header += "200 OK\n"
        header += "Content-Type: text/html\n\n"
        # print(header)
        client_socket.send(header.encode())
        data = get_file_data(CURRENT_DIRECTORY, False)
        # print(data)
        client_socket.send(get_file_data(CURRENT_DIRECTORY, False))
        
    return


# get the payload from the socket ( coming from browser)
# in HTTP the sections are separate by "\r\n\r\n", hence
# each section ( header, form data) are returned separatly
def get_payload(client_socket: socket.socket):
    data = b""
    while b"\r\n\r\n" not in data:
        d = client_socket.recv(1)
        print(d)
        data +=  d
    return data


# main function to serve client requests
def service_client(client_socket: socket.socket) -> None:
    client_request_header = get_payload(client_socket).decode().split()
    print(client_request_header)

    if client_request_header[2] != "HTTP/1.1":
        header = "HTTP/1.1 505 HTTP Version Not Supported\n"
        client_socket.send(header)
    else:
        if client_request_header[0] == "GET":
            handle_get_requests(client_socket, client_request_header[1])
        elif client_request_header[0] == "POST":
            handle_post_requests(client_socket, client_request_header[1])
        elif client_request_header[0] == "DELETE":
            pass
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    return
