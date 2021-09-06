from flask import Flask
from flaskext.mysql import MySQL
from flask import request, jsonify
import pymysql.cursors
connection = pymysql.connect(host='165.22.14.77',
                             user='b27',
                             password='b27',
                             database='syllabusDB',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)



@app.route('/api/syllabus')
def showSyllabus():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM syllabus WHERE userId = 103 AND status = 1")
    results = cursor.fetchall()
    return jsonify(results)

@app.route('/api/syllabus', methods=['POST'])
def insertSyllabus():
    if request.method == "POST":
        payLoad = request.json
        name = payLoad['name']
        description = payLoad['description']
        learningObjectives = payLoad['learningObjectives']
        cursor = connection.cursor()
        insertQuery = "INSERT INTO syllabus(name, description, learningObjectives, userId, status) Values(%s, %s, %s, %s, %s)"
        values = (name, description, learningObjectives, 103, 1)
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

@app.route('/api/syllabus/<syllabusId>', methods=['PUT'])
def updateSyllabus(syllabusId):
    if request.method == "PUT":
        payLoad = request.json
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