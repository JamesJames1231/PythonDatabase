import os
from flask import Flask, request, render_template, send_file, make_response
import shutil
import requests
import database

app = Flask(__name__)
##
#Opening the location file
##
def openFile():
    file = open("./admin/folder.txt", "r")
    path = file.read()
    file.close()
    return path

def searchDir(val):
    #Find all the files in the home directory
    path = openFile()
    files = os.listdir(path)

    return files

##
##Sqlite Databases
##
import sqlite3
con = sqlite3.connect("databases/users.db", check_same_thread=False)
cur = con.cursor()

##
##Creating a sign in cookie
##
def setCookie(id):
    resp = make_response(render_template("home.html", data="A User Was Found With These Details."))
    userID = str(id)
    resp.set_cookie('userID', userID)
    return resp

##
##Checking cookie status
##
def checkCookie():
    value = request.cookies.get('userID')
    if value is None:
        return "LOGIN PLEASE"
    else:
        return "yay you have a cookie"
    
##
##The login page of the website
##
@app.route('/')
def index():
    response = checkCookie()
    print(response)
    if response == "LOGIN PLEASE":
        return render_template('login/login.html')
    else: 
        return render_template("home.html")

##
#This is for when the user attempts to login
##
@app.route('/loginAttempt', methods=['POST'])
def loginAttempt():
    try:
        email = request.form.get("email")
        password = request.form.get("password")

        headers = {
            'Content-Type': 'text/json'
            'accept: text/plain'
        }
        
        url = 'https://userauth-cdb8h0f8hwaseff0.ukwest-01.azurewebsites.net/'
        value = '"jamessrsmith@outlook.com:Rout3rMugPl@nt"'
        
        x = requests.post(url, data=value, headers=headers)
        print(x.text)
        if x.text == "James":
            print("No User Found")
            return render_template("login/login.html", data="No User Was Found With These Details.")
        else:
            print("User Found Succesfully")
            resp = setCookie(x.text)
            return resp
        
    except:
        print("Errors have occoured")
        return render_template("login/login.html", data="An Error Occoured During This Process. Please Try Again.")

##
#This section is for when the user uploads a file
##
@app.route('/fileUpload', methods=['POST'])
def fileUpload():
    
    path = openFile()

    file = request.files['files']
    file.save(os.path.join(path, file.filename))

    #Find all the files in the home directory
    files = searchDir(path)
    
    return render_template('home.html', files=files, searched="File/Folder Has Not Been Found")

##
#This section is for when the user creates a new folder
##
@app.route('/folderCreation', methods=['POST'])
def folderCreation():

    path = openFile()

    folderName = request.form["folderName"]
    newPath = path + "/" + folderName

    #Checking to see if the folder already exists
    if not os.path.exists(newPath):
        os.makedirs(newPath)

        #Find all the files in the home directory
        files = searchDir(path)
    
        return render_template('home.html',  files=files, searched="File/Folder Has Not Been Found")
    
    else:

        #Find all the files in the home directory
        files = searchDir(path)
            
        return render_template('home.html', files=files, searched="File/Folder Has Not Been Found")

##
#This section is for when the user wants to delete a file or folder
##
@app.route('/delete', methods=["GET"])
def delete():

    path = openFile()

    file = request.args.get('file', '')
    toDelete = path + file

    if request.args.get('file', '').find('.') == -1:
        shutil.rmtree(toDelete)
        
        #Find all the files in the home directory
        files = searchDir(path)
        
        return render_template('home.html', files=files, searched="File/Folder Has Not Been Found")
        
    else:
        os.remove(toDelete)

        #Find all the files in the home directory
        files = searchDir(path)
        
        return render_template('home.html', files=files, searched="File/Folder Has Not Been Found")

##    
#This is the section that allows the user to download files
##
@app.route('/downloadFile', methods=['GET'])
def downloadFile():

    path = openFile()

    selectedFile = path + request.args.get('file')

    if request.args.get('file', '').find('.') != -1:
        return send_file(selectedFile, as_attachment=True)
    else:
        #Find all the files in the home directory
        files = searchDir(path)
        zipped = shutil.make_archive(selectedFile, 'zip', selectedFile)
    
        return render_template('home.html', files=files, searched="File/Folder Has Not Been Found")

##
#This is the section that allows the user to access sub-folders
##
@app.route('/subFolder', methods=["POST"])
def subFolder():

    path = openFile()

    #Sending back all files
    newPath = path  + request.form["subFolder"] + "/"
    #Find all the files in the home directory
    files = searchDir(newPath)

    subFolder = open("./admin/folder.txt", "w")
    subFolder.write(newPath)
    subFolder.close()

    return render_template('home.html', files=files, searched="File/Folder Has Not Been Found")

##
#This is the section that allows the user to move 'back to the home directory
##
@app.route('/backFolder', methods=["POST"])
def backFolder():

    path = openFile()

    split = path.split("/")
    
    status = ""
    if(len(split) == 4):

        return render_template("login/login.html")
    
    else:
        split.pop()
        split.pop()

        newPath = ""
        for val in split:
            newPath += val + "/"

        subFolder = open("./admin/folder.txt", "w")
        subFolder.write(newPath)
        subFolder.close()
    
        #Sending back all files
        files = searchDir(newPath)
    
        return render_template('home.html', files=files, searched="File/Folder Has Not Been Found")

##
#This is the section for when the user wants to view their file
##
@app.route("/view", methods=["GET"])
def view():

    imgArray = ["jpg", "jpeg", "png", "svg", "gif", "bmp", "pdf"]
    vidArray = ["mkv", "mpeg", "mpg", "mp4"]
    textArray = ["txt"]

    file = request.args.get('file', '')
    
    find = file.find(".")
    length = len(file)
    ext = length - find - 1


    extension = ""  
    if ext == 3:
        extension += file[-3]
        extension += file[-2]
        extension += file[-1]
    elif ext == 4:
        extension += file[-4]
        extension += file[-3]
        extension += file[-2]
        extension += file[-1]

    readFile = open("./admin/folder.txt", "r")
    path = readFile.read()
    Path = path.lstrip(".")
    readFile.close()

    if extension in imgArray:
        
        finalPath = Path + "/" + file    
        return render_template('viewing/images.html', returnFile=finalPath, image=file)
    
    elif extension in vidArray:
        
        finalPath = Path + "/" + file    
        return render_template('viewing/video.html', returnFile=finalPath, image=file)

    elif extension in textArray:
        
        finalPath = "." + Path + "/" + file
        readFile = open(finalPath)
        value = readFile.readlines()
        values = ""
        for val in value:
            values += val
        readFile.close()
        return render_template('viewing/text.html', returnFile=finalPath, image=file, value=values)

    else:
        files = searchDir(path)
        return render_template('home.html', files=files, error="Unsupported File Format", searched="File/Folder Has Not Been Found")


##
#This section is for when the user returns from viewing a file
##
@app.route("/returning", methods=["POST"])
def returning():
    path = openFile()
    files = searchDir(path)
    return render_template('home.html', files=files, error="Unsupported File Format", searched="File/Folder Has Not Been Found")

##
##Index Page
##
@app.route('/home')
def home():
    response = checkCookie()
    print(response)
    if response == "LOGIN PLEASE":
        return render_template('login/login.html')
    else: 
        return render_template("home.html")

##
#This is the section that begins the server on the localhost on PORT 5000
##
if __name__ == '__main__':
    database.folderCreation()
    app.run(debug=True, host='0.0.0.0')
