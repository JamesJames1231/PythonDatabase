from flask import Flask, request, render_template, send_file, make_response
import sqlite3
import os
import shutil
import database
import create_user
from logging import FileHandler,WARNING
app = Flask(__name__)

def getCookie():
    return request.cookies.get('user')

###########################
##Connection to databases##
###########################
def databaseCon():
    value = request.cookies.get('user') or "/admin"
    connectString =f"databases{value}/nav.db"
    print(connectString)
    ##connectString = "databases" + value + "/nav.db"
    return sqlite3.connect(connectString)
def userDatabase():
    return sqlite3.connect("databases/users.db")
def dataCon():
    value = request.cookies.get('user')
    connectString = "databases" + value + "/data.db"
    return sqlite3.connect(connectString)
############################
#Section End################
############################
#
#
#
#
#############################
##Creating a sign in cookie##
#############################
def setCookie(name):
    pathName = "/" + name
    location = currentLocation()
    resp = make_response(render_template("homepage/index.html", data="Login Successful.", location=location[0]))
    resp.set_cookie('user', pathName, max_age=86400)
    return resp

##########################
##Checking cookie status##
##########################
def checkCookie():
    value = request.cookies.get('user')
    if value is None:
        return 0
    else:
        return 1
    
##################
##Final location##
##################
def finalLocation():
    location = currentLocation()
    user = request.cookies.get('user')
    print(user)
    finalLocation = ""
    finalLocation = "./static/directory" + user + location[0]
    return finalLocation

#################################
##The login page of the website##
#################################
@app.route('/')
@app.route('/home')
def index():
    try:
        response = checkCookie()
        if response == 0:
            return render_template('login_page/index.html')
        elif response == 1:
            finLocation = finalLocation()
            files = os.listdir(finLocation)
            location = currentLocation()
            return render_template("homepage/index.html", files=files, location=location[0])
    except Exception as error:
        return error
    
##############################################
#This is for when the user attempts to login##
##############################################
@app.route('/loginAttempt', methods=['POST'])
def loginAttempt():
    email = request.form.get("email")
    password = request.form.get("password")
    
    con = userDatabase()
    cur = con.cursor()
    sql = "SELECT name FROM users WHERE email = ? AND password = ? LIMIT 1"
    cur.execute(sql, (email, password))
    response = cur.fetchone()
    con.commit()
    con.close
    
    print(response)
    if not response:
        return render_template("login_page/index.html", data="Login Unsucsessful.")
    else:
        resp = setCookie(response[0])
        return resp
####################################
##Section End#######################
####################################
#
#
#
#
############################
##Finding current location##
############################
def currentLocation():
    sql = "SELECT location FROM nav ORDER BY id DESC LIMIT 1"
    con = databaseCon()
    cur = con.cursor()
    cur.execute(sql)
    response = cur.fetchone()
    con.commit()
    con.close
    return response

#########################
##Navigation controller##
#########################
def navigation(type, name):
    response = currentLocation()
    try:
        con = databaseCon()
        cur = con.cursor()
        if type == "home":
            sqlHome = "INSERT INTO nav (location) VALUES ('/')"
            cur.execute(sqlHome)
            con.commit()
            con.close()
            return index()
        elif type == "foward":
            location = response[0]
            if location == '/':
                newLocation = location + name
                newLocation = str(newLocation)
            else:
                newLocation = location + "/" + name
                newLocation = str(newLocation)
            sqlHome = "INSERT INTO nav (location) VALUES (?)"
            cur.execute(sqlHome, (newLocation,))
            con.commit()
            con.close()
            return index()
        else:
            location = response[0]
            if location == '/':
                return resp("Nothing Back There Pal.")
            else:
                splitLocation = location.split("/")
                splitLocation.pop()
                if splitLocation[0] == "" and len(splitLocation) == 1:
                    newLocation = "/"
                else:
                    newLocation = ""
                    counter = 0
                    for x in splitLocation:
                        if counter == 0:
                            counter = counter + 1
                            continue
                        newLocation += "/"
                        newLocation += x
                sqlHome = "INSERT INTO nav (location) VALUES (?)"
                cur.execute(sqlHome, (newLocation,))
                con.commit()
                con.close()
                return index()
    except Exception as error:
        ##Error code: Complete faliure
        return error   
####################################
##Section End#######################
####################################
#
#
#
#    
#####################################
##Returning to the page with errors##
#####################################
def resp(errors):
    finLocation = finalLocation()
    files = os.listdir(finLocation)
    location = currentLocation()
    return render_template("homepage/index.html", files=files, error=errors, location=location[0])

#######################
##Create new user######
#######################
@app.route('/userCreation', methods=['POST'])
def userCreation():
    name = ""
    email = ""
    password = ""
    try:
        sql = "SELECT name FROM users WHERE name = ? LIMIT 1"
        con = databaseCon()
        cur = con.cursor()
        cur.execute(sql, (name,))
        response = cur.fetchone()
        con.commit()
        con.close
        if not response: 
            databaseAdd = create_user.addUser(name, email, password)
            if databaseAdd == 1:
                addFolder = create_user.createFolder(name)
                if addFolder == 1:
                    return index()
                else: 
                    return resp("Database Failed, Try Again.")
            else: 
                return resp("Database Failed, Try Again.")
        else:
            return resp("Name Already Taken, Try Again.")
    except:
        return resp("Name Already Taken, Try Again.")

#######################
##Uploading a file to##
#######################
@app.route('/fileUpload', methods=['POST'])
def fileUpload():
    file = request.files['files']
    filename = file.filename
    
    location = finalLocation()
    checkLocation = location + "/" + filename
    print(checkLocation)
    if not os.path.exists(checkLocation):
        locationTwo = currentLocation()
        response = database.fileCreation(filename, locationTwo[0])
        
        if response == 1:
            file.save(os.path.join(location, file.filename))
            return index()
        else:
            return resp("File Could Not Be Uploaded To Database.")
    else:
        return resp("File Name Already Taken.")
    
#####################
##Creating a folder##
#####################
@app.route('/folderCreation', methods=['POST'])
def createFolder():
    folderName = request.form["folderName"]
    location = finalLocation()
    checkLocation = location + "/" + folderName
    print(checkLocation)
    
    if not os.path.exists(checkLocation):
        location = currentLocation()
        response = database.folderCreation(folderName, location[0])
        if response == 1:
            os.makedirs(checkLocation)
            return index()
        else:
            return str(response)
    else:
        return resp("Folder Name Taken")
    
##########################
##Deleting files/folders##
##########################
@app.route('/delete', methods=["GET"])
def delete():
    file = request.args.get('file', '')
    location = finalLocation()
    todelete = location + file
    
    if request.args.get('file', '').find('.') == -1:
        ##CURRENTLY UNABLE TO DELETE FOLDERS LOL 
        return index()
    else:
        local = currentLocation()
        response = database.deleteFiles(file, local[0])
        if response == 1:
            newLocal = finalLocation()
            newLocal = newLocal + '/' + file
            os.remove(newLocal)
            return index()
        else:
            return resp("Could Not Remove File From Database.")
####################################
##Section End#######################
####################################
#        
#       
#
#
######################
##Navigation options##
######################
@app.route('/backFolder', methods=["POST"])
def backFolder():
    return navigation("back", "NOTNEEDED")

@app.route('/subFolder', methods=["POST"])
def subFolder():
    subfolder = request.form["subFolder"]
    return navigation("foward", subfolder)

@app.route('/returnHome', methods=['POST', 'GET'])
def returnHome():
    return navigation("home", "NOTNEEDED")