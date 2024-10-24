import app
import os
import sqlite3
##
##Add user to the database
##
def addUser(name, email, password):
    try:
        con = app.userDatabase()
        cur = con.cursor()
        sql = "INSERT INTO users (name, email, password) VALUES (?, ?, ?)"
        cur.execute(sql, (name, email, password))
        con.commit()
        con.close
        return 1
    except:
        ##Error code: Failed to add new user
        return 0

def createFolder(name):
    try:
        string = "./static/directory/" + name
        os.makedirs(string)
        newString = "./databases/" + name
        os.makedirs(newString)
        try:
            string1 = "./databases/" + name + "/data.db"
            string2 = "./databases/" + name + "/nav.db"
            
            dataCon = sqlite3.connect(string1)
            navCon = sqlite3.connect(string2)
            try:
                sqlNav = """CREATE TABLE nav (id INTEGER PRIMARY KEY AUTOINCREMENT, location TEXT NOT NULL);"""
                sqlNav2 = "INSERT INTO nav (location) VALUES ('/');"
                navCur = navCon.cursor()
                navCur.execute(sqlNav)
                navCur.execute(sqlNav2)
                navCon.commit()
                navCon.close
                
                sqlData = """CREATE TABLE files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    folderid INTEGER NOT NULL
                )"""
                sqlData2 = """CREATE TABLE folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    foldername TEXT NOT NULL,
                    folderlocation TEXT NOT NULL
                )"""
                sqlData3 = """CREATE TABLE deleted (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deletedname TEXT NOT NULL,
                    originID INTEGER NOT NULL
                )
                """
                dataCur = dataCon.cursor()
                dataCur.execute(sqlData)
                dataCur.execute(sqlData2)
                dataCur.execute(sqlData3)
                dataCon.commit()
                dataCon.close
            except:
                ##Failed to fill the database tables
                return 3
        except:
            ##Error code: couldnt create files
            return 2
        return 1
    except:
        ##Error code: failed to create folder
        return 0