import sqlite3
import app
##
##Find details about currently selected file/folder
##
def findDetails(type, name, location):
    try:
        con = app.dataCon()
        cur = con.cursor()
        if type == "file":
            sql = "SELECT * FROM files WHERE filename = ? AND folderid = ?"
            cur.execute(sql, (name, location))
            rec2 = cur.fetchone()
            con.commit()
            con.close()
            return rec2
        elif type == "folder":
            sql = "SELECT * FROM folders WHERE foldername = ? AND id = ?" 
            cur.execute(sql, (name, location))
            rec2 = cur.fetchone()
            con.commit()
            con.close()
            return rec2
        else:
            sql = "SELECT * FROM deleted WHERE deletedname = ? LIMIT 1" 
            cur.execute(sql, (name,))
            rec2 = cur.fetchone()
            con.commit()
            con.close()
            return rec2
    except: 
        ##Error code: Absolute faliure
        return 0


##
##Create a brand new table
##
def tableCreation(sql):
    try:
        con = app.dataCon()
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()
        return 1
    except:
        ##Error code: did not create new table
        return 0


##
##Create a new folder
##
def folderCreation(foldername, pagelocation):
    sql = "INSERT INTO folders (foldername, folderlocation) VALUES (?, ?);"
    try:
        con = app.dataCon()
        cur = con.cursor()
        cur.execute(sql, (foldername, pagelocation))
        con.commit()
        con.close()
        return 1
    except Exception as error:
        ##Error code: did not create new folder
        return error


##
##Create a new file
##
def fileCreation(filename, pagelocation):
    sql = "INSERT INTO files (filename, folderid) VALUES (?, (SELECT id FROM folders WHERE folderlocation = ?))"
    try:
        con = app.dataCon()
        cur = con.cursor()
        cur.execute(sql, (filename, pagelocation))
        con.commit()
        con.close()
        return 1
    except Exception as error:
        ##Error code: did not create new file
        return error
    

##
##Delete any FILE 
##
def deleteFiles(filename, pagelocation):
    try:
        preSQL = "INSERT INTO deleted (deletedname, originID) VALUES (?, (SELECT id FROM folders WHERE folderlocation = ?))"
        sql = "DELETE FROM files WHERE id = (SELECT id FROM files WHERE filename = ? AND folderid = (SELECT id FROM folders WHERE folderlocation = ?))"
        con = app.dataCon()
        cur = con.cursor()
        cur.execute(sql, (filename, pagelocation))
        cur.execute(preSQL, (filename, pagelocation))
        con.commit()
        con.close()
        return 1
    except Exception as error:
        ##Error code: did not delete file or did not copy deleted file into deleted folder
        print(error)
        return 0


##
##Perma delete files in the deleted folder
##
def deleteDeleted(filename):
    deletedDetails = findDetails("deleted", filename, "NOT NEEDED")
    try:
        sql = "DELETE FROM deleted WHERE id = (SELECT id FROM deleted WHERE deletedname = ? AND originID = ?)"
        con = app.dataCon()
        cur = con.cursor()
        cur.execute(sql, (filename, deletedDetails[2]))
        con.commit()
        con.close()
        return 1
    except: 
        ##Error code: file in deleted folder has not been deleted
        return 0


##
##Recover deleted files from the deleted folder
##  
def recoverDeletedFile(filename):
    deletedDetails = findDetails("deleted", filename, "NOT NEEDED")
    try:
        try:
            sql = "SELECT * FROM folders WHERE id = ?"
            con = app.dataCon()
            cur = con.cursor()
            cur.execute(sql, (deletedDetails[0],))
            records = cur.fetchone()
            con.commit()
            con.close()
            if not records:
                ##Error code: No Folder Found
                return 3
            else:
                sql = "SELECT deletedname FROM deleted WHERE id = ? LIMIT 1"
                con = app.dataCon()
                cur = con.cursor()
                cur.execute(sql, (deletedDetails[0],))
                rec2 = cur.fetchone()
                con.commit()
                con.close()
                try:
                    response = fileCreation(rec2[0], records[2])
                    if response == 0:
                        deleteResponse = deleteDeleted(rec2[0], deletedDetails[2])
                        if deleteResponse == 0:
                            ##Success code
                            return 1 
                        else: 
                            ##Error code: File not deleted from deleted folder
                            return 7
                    else:
                        ##Error code: Failed to insert old file
                        return 6
                except:
                    ##Error code: Failed to call other function
                    return 5
        except:
            ##Error code: Failed to complete SQL search
            return 4
    except:
        ##Error code: Everything has broken 
        return 2 


##
##Delete a folder and any sub-content
##
def deleteFolder():
    try:
        return 1
    except:
        ##Error code: Folder was not deleted
        return 0