import json
from flask import Flask, request, jsonify
import jwt
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
mongo = PyMongo(app)

projectLen = 0
foldStructure = {}


@app.route("/", methods=["POST", "GET"])
def signIn_user():

    currentCollection = mongo.db.user

    pwd = request.form.get("pwd")
    name = request.form.get("name")

    # hash = generate_password_hash(pwd)

    data = currentCollection.find_one({"name": name, "pwd": pwd})
    if data :
        token = jwt.encode({"name": name, "pwd": pwd}, "secret", algorithm="HS256")
        return jsonify({"success":True,"token": token, "name": name,"message": "Sign in successful!"})
    else:
        return jsonify({"success":False,"message":"Invalid User Name or password"})


@app.route("/home", methods=["POST", "GET"])
def projectView():

    currentCollection = mongo.db.project

    global projectLen
    if request.method == "POST":

        projects = request.form.get("projects")
        uname = request.form.get("uname")

        strName = f"{uname}"

        data = currentCollection.find_one({"uName": strName})
        if data:
            id = data["_id"]
            newvalues = {"$set": {"projects": projects}}
            currentCollection.update_one({"_id": id}, newvalues)
            oldData = currentCollection.find_one({"uName": uname})
            projectLen = oldData["projects"]

        else:
            projects_record = {"uName": uname, "projects": projects}
            currentCollection.insert_one(projects_record)
            newData = currentCollection.find_one({"uName": uname})
            projectLen = newData["projects"]

    elif request.method == "GET":
        uname = request.args.get("uname")
        strName = f"{uname}"

        data = currentCollection.find_one({"uName": strName})

        if data:
            projectLen = data["projects"]
        else:
            projectLen = 0

    return str(projectLen)


@app.route("/projectView", methods=["POST", "GET"])
def saveProjectStructure():
    currentCollection = mongo.db.projectStructure

    if request.method == "POST":

        projectName = request.form.get("projectName")
        uname = request.form.get("uname")
        frontend = request.form.get("frontendFoldStruct")
        backend = request.form.get("backendFoldStruct")

        frontendStructConvertObj = json.loads(frontend)
        backendStructConvertObj = json.loads(backend)

        strName = f"{uname}"
        pName = f"{projectName}"

        data = currentCollection.find_one({"uName": strName, "projectName": pName})

        if data:

            id = data["_id"]
            newvalues = {
                "$set": {
                    "frontendStruct": frontendStructConvertObj,
                    "backendStruct": backendStructConvertObj,
                }
            }
            currentCollection.update_one({"_id": id}, newvalues)

        else:

            projects_record = {
                "projectName": projectName,
                "uName": uname,
                "frontendStruct": frontendStructConvertObj,
                "backendStruct": backendStructConvertObj,
            }
            currentCollection.insert_one(projects_record)

        foldStructure = currentCollection.find_one(
            {"uName": strName, "projectName": pName}, {"_id": 0}
        )

    elif request.method == "GET":
        uname = request.args.get("uname")
        projectName = request.args.get("projectName")

        strName = f"{uname}"
        pName = f"{projectName}"

        foldStructure = currentCollection.find_one(
            {"uName": strName, "projectName": pName}, {"_id": 0}
        )

    return jsonify(foldStructure)


if __name__ == "__main__":
    app.run(debug=True)
