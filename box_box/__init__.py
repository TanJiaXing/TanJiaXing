from flask import Flask, render_template, flash, url_for, session, redirect, request, send_file
from sqlalchemy import text  # New
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from Forms import LoginForm, UploadForm
from werkzeug.utils import secure_filename
from io import BytesIO
from cryptography.fernet import Fernet


app = Flask(__name__)

app.config["SECRET_KEY"] = b'o5Dg987*&G^@(E&FW)}'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)
app.config["SESSION_TYPE"] = 'sqlalchemy'
app.config["SESSION_SQLALCHEMY"] = db
sess = Session(app)


# SQL Tables
class Users(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    password_age = db.Column(db.DateTime)
    clearance = db.Column(db.String, nullable=False)
    department = db.Column(db.String)
    workgroup = db.Column(db.String)
    status = db.Column(db.String)
    last_active_date = db.Column(db.DateTime)


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50), nullable=False)
    # filetype = db.Column(db.String(50))
    data = db.Column(db.LargeBinary, nullable=False)
    owner = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String, nullable=False)
    classification = db.Column(db.Integer, nullable=False)


#     shared_with = db.Column(db.String)
#     size = db.Column(db.String)
#     comments = db.Column(db.String)


@app.route('/', methods=['GET', 'POST'])
def home():
    # try:
    #     if not session['user']:
    #         return redirect(url_for('login'))
    # except KeyError:
    #     return redirect(url_for('login'))
    try:
        if session['user']:
            files = Files.query.all()
            uploadform = UploadForm(request.form)
            return render_template('home.html', files=files, uploadform=uploadform)
    except KeyError:
        return redirect(url_for('login'))


# Login system
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        # # Parameterized queries
        # sql_username = text("Select * from Users where email = :x")
        # c2 = db.engine.execute(sql_username, x=form.email.data)
        # user = None
        # for i in c2:
        #     user = i
        user = Users.query.filter_by(email=form.Email.data).first()
        if user:
            if user.password == form.Password.data:
                session['user'] = user
                print(session['user'].name)
                flash(f'{user.name} has logged in!',
                      'success')
                return redirect(url_for('home'))
        flash('Incorrect username or password', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# File Related
@app.route('/uploads', methods=['POST']) #MethodFernet
def upload():
    form = UploadForm(request.form)
    if request.method == 'POST':
        file = request.files['File']
        data = file.read()                          #JX
        print (data)                                #JXCheck
        data = FernetEncrypting(data)               #JX
        print("Unencrypted to Decrypted Separator") #JXCheck
        print (data)                                #JXCheck

        fileItem = Files(filename=file.filename, data=data, owner=session["user"].name, status="active",
                         classification=form.Class.data)
        db.session.add(fileItem)
        db.session.commit()
        flash(f'{file.filename} has been saved!', 'success')
        return redirect(url_for('home'))
    return render_template('home.html', form=form)


@app.route('/downloads/<id>', methods=['POST', 'GET']) #MethodFernet
def download(id):
    file = Files.query.filter_by(id=id).first()
    Data = file.data                            #JX
    print (Data)                                #JXCHECK
    print ("Before Decrypting After Calling")   #JXCHECK
    DecryptedData = FernetUnecrypting(Data)     #JX
    print ("After calling")                     #JXCHECK
    print (DecryptedData)                       #JXCHECK
    return send_file(BytesIO(Data), as_attachment=True, attachment_filename=file.filename)




@app.route('/remove/<id>', methods=['POST', 'GET'])
def remove(id):
    file = Files.query.filter_by(id=id).first()
    if file.status == "active":
        file.status = "deleted"
        flash(f'{file.filename} has been moved to Recycle Bin!', 'success')
    else:
        db.session.delete(file)
        flash(f'{file.filename} has been permanently removed!', 'success')
    db.session.commit()
    return redirect(url_for('home'))



def FernetEncrypting(data):
    f = Fernet(key)
    encrypting = f.encrypt(data)
    return encrypting

def FernetUnecrypting(data):
    f = Fernet(key)
    decrypting = f.decrypt(data)
    return decrypting

app = Flask(__name__)
db.create_all()
with open('mykey.key', 'rb') as mykey:  # JX
    key = mykey.read()  # JX

if __name__ == '__main__':
    app.run(debug=True)

