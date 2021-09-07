from unicodedata import is_normalized
from dns.message import Message
from flask import Flask
from flask import request, jsonify
import pymysql.cursors
import uuid
import re
from email_validator import validate_email, EmailNotValidError
connection = pymysql.connect(host='165.22.14.77',
                            user='b27',
                            password='b27',
                            database='syllabusDB',
                            cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)
@app.before_request
def validateToken():
    print(uuid.uuid4())
    path = request.path
    print(path)
    print("First request")
    if((path != "/api/signin") and (path != "/api/signup")):
        token = request.headers['Authorization']
        setattr(request, "token", token)
        if(token == ""):
            return {"Error": "Unauthorized User"}, 401

@app.before_request
def validateUserId():
    path = request.path
    if(path != "/api/signin" and path != "/api/signup"):
        sql = "Select userId from users where token = %s"
        token = request.token
        value = (token)
        cursor = connection.cursor()
        status = cursor.execute(sql, value)
        results = cursor.fetchall()
        if (status == 1):
            userId = results[0]['userId']
            setattr(request, "userId", userId)
        else:
            return {"Error": "Unauthorized User"}, 401

@app.route('/api/signin', methods=['POST'])
def signIn():
    if request.method == "POST":
        payLoad = request.json
        userName = payLoad['userName']
        password = payLoad['password']
        cursor = connection.cursor()
        insertQuery = "SELECT token from users where userName = %s and password = %s"
        values = (userName, password)
        status = cursor.execute(insertQuery, values)
        results = cursor.fetchall()
        if (status == 1):
            return jsonify(results)
        else:
            return {"Message": "Invalid UserName/Password"}, 400

@app.route('/api/signup', methods=['POST'])
def signUp():
    if request.method == "POST":
        payLoad = request.json
        userName = payLoad['userName']
        password = payLoad['password']
        try:
            isEmailValid = validate_email(userName)
        except EmailNotValidError as e:
            print(e)
            return {"Message": str(e)}, 400
        if isEmailValid:
            regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
            pattern = re.compile(regex)                
            match = re.search(pattern, password)
            if (match):
                token = str(uuid.uuid4())
                cursor = connection.cursor()
                insertQuery = "INSERT INTO users(userName, password, token) Values(%s, %s, %s)"
                values = (userName, password, token)
                status = cursor.execute(insertQuery, values)
                if(status == 1):
                    return {"message": "Signed Up successfully"}, 201
            else:
                return {"Message": 'Your Password is week.password should contain aleast 6 characters, one special character($, #, @, &) and one digit.'}, 400
        
@app.route('/api/syllabus')
def showSyllabus():
    userId = request.userId
    cursor = connection.cursor()
    value = (userId)
    sql = "SELECT * FROM syllabus WHERE userId = %s AND status = 1"
    cursor.execute(sql, value)
    results = cursor.fetchall()
    return jsonify(results)

def formValidations(payLoad):
    isValid = True
    errorsMessages = {}
    if payLoad['name'] == "" or payLoad['name'] == None:
        errorsMessages["name"] = "Name is required"
        isValid = False
    if payLoad['description'] == "":
        errorsMessages["description"] = "Description is required"
        isValid = False
    if payLoad['learningObjectives'] == "":
        errorsMessages["learningObjectives"] = "DearningObjectives is required"
        isValid = False
    if not isValid:
        errorsMessages["isFormValid"] = False
    else:
        errorsMessages["isFormValid"] = True
    return errorsMessages

@app.route('/api/syllabus', methods=['POST'])
def insertSyllabus():
    if request.method == "POST":
        userId = request.userId
        payLoad = request.json
        print(payLoad)
        try:
            errorMessagesObj = formValidations(payLoad)
            if(errorMessagesObj['isFormValid']):
                name = payLoad['name']
                description = payLoad['description']
                learningObjectives = payLoad['learningObjectives']
                cursor = connection.cursor()
                insertQuery = "INSERT INTO syllabus(name, description, learningObjectives, userId, status) Values(%s, %s, %s, %s, %s)"
                values = (name, description, learningObjectives, userId, 1)
                status = cursor.execute(insertQuery, values)
                connection.commit()
                if (status == 1):
                    id = cursor.lastrowid
                    sql = "SELECT * FROM syllabus WHERE id = %s"
                    value = (id)
                    cursor.execute(sql, value)
                    results = cursor.fetchall()
                    return jsonify(results), 201
                else:
                    return {"Message": "Resourses not found"}, 404
            else:
                del errorMessagesObj["isFormValid"]
                return errorMessagesObj, 400
        except TypeError as e:
            print(e)
            return {"Message": "Please provide the field" + str(e)}, 400
        except KeyError as e:
            print(e)
            return {"Message": "Please provide the field" + str(e)}, 400
        
@app.route('/api/syllabus/<syllabusId>', methods=['PUT'])
def updateSyllabus(syllabusId):
    if request.method == "PUT":
        payLoad = request.json
        try:
            errorMessagesObj = formValidations(payLoad)
            if(errorMessagesObj['isFormValid']):
                name = payLoad['name']
                description = payLoad['description']
                learningObjectives = payLoad['learningObjectives']
                cursor = connection.cursor()
                insertQuery = "UPDATE syllabus SET name = %s, description = %s, learningObjectives = %s where id = %s"
                values = (name, description, learningObjectives, syllabusId)
                status = cursor.execute(insertQuery, values)
                connection.commit()
                if (status == 1):
                    id = syllabusId
                    sql = "SELECT * FROM syllabus WHERE id = %s"
                    value = (id)
                    cursor.execute(sql, value)
                    results = cursor.fetchall()
                    return jsonify(results), 200
                else:
                    return {"Message": "Resourses not found"}, 404
            else:
                del errorMessagesObj["isFormValid"]
                return errorMessagesObj, 400
        except KeyError as e:
            return {"Message": "Please provide the field" + str(e)}, 400
        except TypeError as e:
            print(e)
            return {"Message": str(e)}, 400

@app.route('/api/syllabus/<syllabusId>', methods=['DELETE'])
def deleteSyllabus(syllabusId):
    if request.method == "DELETE":
        cursor = connection.cursor()
        insertQuery = "UPDATE syllabus SET status = 0 where id = %s"
        values = (syllabusId)
        status = cursor.execute(insertQuery, values)
        connection.commit()
        if (status == 1):
            return {"Message": "Syllabus Item  Deleted"}, 200
        else:
            return {"Message": "Resourses not found"}, 404

@app.route('/api/syllabus/<syllabusId>', methods=['GET'])
def searchSyllabus(syllabusId):
    if request.method == "GET":
        id = syllabusId
        cursor = connection.cursor()
        sql = "SELECT * FROM syllabus WHERE id = %s"
        value = (id)
        status = cursor.execute(sql, value)
        print(status)
        results = cursor.fetchall()
        print(results)
        if status == 1:
            return jsonify(results), 200
        else:
            return {"Message": "Resourses not found"}, 404