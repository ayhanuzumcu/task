import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
import pymongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = str(os.environ.get("MONGO_DBNAME"))
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
myclient = pymongo.MongoClient(app.config["MONGO_URI"])
mydb = myclient[app.config["MONGO_DBNAME"]]

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    # myclient = pymongo.MongoClient(app.config["MONGO_URI"])

    # mydb = myclient[app.config["MONGO_DBNAME"]]

    mycol = mydb["tasks"]

    tasks = list(mycol.find())

    return render_template("tasks.html", tasks=tasks)
    # return "hello"



@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    mycol = mydb["tasks"]
    tasks = list(mycol.find({"$text": {"$search": query}}))
    return render_template("tasks.html", tasks=tasks)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        mycol = mydb["users"]
        existing_user = mycol.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        # mongo.db.users.insert_one(register)
        mycol = mydb["users"]
        mycol.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        mycol = mydb["users"]
        existing_user = mycol.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    mycol = mydb["users"]
    username = mycol.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        task = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }
        mycol = mydb["tasks"]
        mycol.insert_one(task)  
        flash("Task Successfully Added")
        return redirect(url_for("get_tasks"))
    mycol = mydb["category"]
    categories = mycol.find().sort("category_name", 1)
    return render_template("add_task.html", categories=categories)


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }

        mycol = mydb["tasks"]
        mycol.update_one({"_id": ObjectId(task_id)}, { "$set": submit })
        flash("Task Successfully Updated")
        
    # mycol = mydb["tasks"]
    task = mydb["tasks"].find_one({"_id": ObjectId(task_id)})

     # mycol = mydb["category"]
    categories = mydb["category"].find().sort("category_name", 1)
    return render_template("edit_task.html", task=task, categories=categories)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mydb["tasks"].delete_one({"_id": ObjectId(task_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))


@app.route("/get_categories")
def get_categories():
    categories = list(mydb["category"].find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        
        category = {
            "category_name": request.form.get("category_name")
        }
        mydb["category"].insert_one(category)  
        flash("Category Successfully Added")
        return redirect(url_for("get_categories"))
    
    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
       
        sub = {
            "category_name": request.form.get("category_name"),
            }

        mydb["category"].update_one({"_id": ObjectId(category_id)}, { "$set": sub })
        flash("Category Successfully Updated")
        
    # mycol = mydb["tasks"]
    category = mydb["category"].find_one({"_id": ObjectId(category_id)})

     # mycol = mydb["category"]
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mydb["category"].delete_one({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)