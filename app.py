from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

def test(a=0):
  if a == 0:
    global tests
  tests = []
test(0)
def reset(a=0):
  if a == 0:
    global oranges
  oranges = []
reset(0)

questioned = [['1+1','2','1','3'],['2+2','3','4','6'],['3+3', '1','2','6']]

class questions:
  def __init__(self, question, answer1, answer2, answer3):
    self.q = question
    self.a1 = answer1
    self.a2 = answer2
    self.a3 = answer3

question1 = questions('what is 1+0', '1', '2', '3')
question2 = questions('what is 1+1', '1', '2', '3')
question3 = questions('what is 1+2', '1', '2', '3')

app = Flask(__name__)
app.secret_key = "oranges"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=.5)

db = SQLAlchemy(app)

class users(db.Model):
  _id = db.Column("id", db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  email = db.Column(db.String(100))

  def __init__(self, name, email):
    self.name = name
    self.email = email

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/view")
def view():
  return render_template("view.html", values=users.query.all())

@app.route("/login", methods=["POST", "GET"])
def login():
  if request.method == "POST":
    session.permanent = True
    user = request.form["nm"]
    session["user"] = user

    found_user = users.query.filter_by(name=user).first()
    if found_user:
      session["email"] = found_user.email
    else:
      usr = users(user, "")
      db.session.add(usr)
      db.session.commit()
      
    flash("login successful??")
    return redirect(url_for('user'))
  else:
    if "user" in session:
      flash("already logged in")
      return redirect(url_for("user"))
    return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
  email = None
  if "user" in session:
    user = session["user"]

    if request.method == "POST":
      email = request.form["email"]
      session["email"] = email
      found_user = users.query.filter_by(name=user).first()
      found_user.email = email
      db.session.commit()
      flash("email not stolen")
    else:
      if "email" in session:
        email = session["email"]
      
    return render_template('user.html', usern=user, email=email)
  else:
    flash("not logged in", "info")
    return redirect(url_for("login"))

@app.route('/logout')
def logout():
  flash("you have been logged out", "info")
  session.pop("user", None)
  session.pop("email", None)
  session.pop("answer", None)
  return redirect(url_for("login"))

@app.route("/survey", methods=["POST", "GET"])
def survey():
  reset()
  if request.method == "POST":
    f = request.form
    for key in f.keys():
      for value in f.getlist(key):
        oranges.append(value)
        print(key,":",value)
    session['answer'] = oranges
    return redirect(url_for('answer'))
  else:
    if "user" in session and "answer" in session:
      flash("already done")
      return redirect(url_for("answer"))
    return render_template("survey.html", lists=questioned)

@app.route("/answer")
def answer():
  if "answer" in session:
    oranges = session['answer']
    return render_template("answer.html", answers=oranges)
  else:
    return redirect(url_for("survey"))
      
@app.route("/css")
def css():
  return render_template("csstest.html")

db.create_all()
app.run(host='0.0.0.0', port=8080, debug=True)