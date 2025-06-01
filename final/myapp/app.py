from flask import Flask, redirect, flash, render_template, jsonify, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_debugtoolbar import DebugToolbarExtension
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib 
import uuid  
from PIL import Image, ImageDraw, ImageFont
from email.mime.image import MIMEImage
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv
from flask_migrate import Migrate


# Load environment variables from a .env file if it exists
load_dotenv("details.env")

# Initialize Flask app
app = Flask(__name__)

# Configure the Flask app with SQLAlchemy
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  # Optional, based on your use case
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5432/foxdata')


# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Optional: If you need the engine directly for specific tasks
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    from sqlalchemy import create_engine
    engine = create_engine(DATABASE_URL)

try:
    with app.app_context():
        db.session.execute(text('SELECT 1'))
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")

app.debug = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class Gift(db.Model):
    __tablename__ = 'gifts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(255), nullable=False)  # Add the missing 'code' column
    status = db.Column(db.String(255), nullable=False)
    validation = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<Gift {self.username}>'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)  
    hash = db.Column(db.String(255), nullable=False)       
    date = db.Column(db.DateTime(timezone=False), nullable=True)  
    admin = db.Column(db.Boolean, default=False)          
    email = db.Column(db.String(255), nullable=False)      
    validation = db.Column(db.String(255), nullable=True)  
    reset = db.Column(db.String(255), nullable=True)       
    timestamp = db.Column(db.DateTime(timezone=False), default=datetime.utcnow)  

    def __repr__(self):
        return f'<User {self.username}>'

class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.String, nullable=False)
    booked = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Schedule(id={self.id}, date={self.date}, time={self.time}, availability={self.availability}, booked={self.booked}, user={self.user})>"

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def home():
    reviews = db.session.execute(text("SELECT * FROM reviews")).fetchall()
    total = db.session.execute(text("SELECT COUNT(*) FROM reviews")).scalar()
    if 'user_id' in session:
        user = session.get("user")
        return render_template ("/index.html", admin=session.get('admin', False), reviews=reviews, total=total, user=user)
    else:
        return render_template ("/index.html", admin=session.get('admin', False), reviews=reviews, total=total)

@app.route("/massage", methods=["GET", "POST"])
def swedish():
    if request.method == "POST":
        massage = request.form['massage'] 
        user = session.get("user") if 'user_id' in session else None
        admin = session.get('admin', False)
        
        templates = {
            "swedish": "swedish.html",
            "specialist": "specialist.html",
            "iastm": "iastm.html"
        }
        
        if massage in templates: 
            return render_template(templates[massage], admin=admin, user=user)
    
    return redirect("/")   

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not request.form.get("username"):
            flash("Must provide username 403")
            return render_template("login.html", admin=session.get('admin', False))

        elif not request.form.get("password"):
            flash("must provide password 403")
            return render_template("login.html", admin=session.get('admin', False))

        user = User.query.filter_by(username=username).first()
        
        if user is None or not check_password_hash(user.hash, password):
            flash("Invalid username and/or password", "error")
            return render_template("login.html", admin=session.get('admin', False))
        # Set user_id in session
        session["user_id"] = user.id

        # Fetch the username and set it in the session
        result = db.session.execute(text("SELECT username FROM users WHERE id = :id"), {"id": session["user_id"]})
        session["user"] = result.scalar()

        # Fetch the admin status and process it
        result = db.session.execute(text("SELECT admin FROM users WHERE id = :id"), {"id": session["user_id"]})
        admin_status = result.scalar()  # .scalar() returns a single value from the result set

        # Optionally, set the admin status in session
        session["admin"] = admin_status
        return redirect("/")

    else:
        return render_template("login.html", admin=session.get('admin', False))
    
@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")

#@app.route("/register", methods=["GET", "POST"])
def register():
        if request.method == "POST":
            username = request.form.get("username")
            userCheck = User.query.filter_by(username=username).first()
            if userCheck:
                flash("Username already taken")
                return render_template("register.html")          
            if not username:
                flash("Please enter a username")
                return render_template("register.html")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            if not password:
                flash("Please enter a password")
                return render_template("register.html")
            if password != confirmation:
                flash("Passwords don't match")
                return render_template("register.html")
            email = request.form.get("email")
            emailCheck = User.query.filter_by(email=email).first()
            if emailCheck:
                flash("Email already taken")
                return render_template("register.html")
            if not email:
                flash("Please enter an email")
                return render_template("register.html")
            hash = generate_password_hash(password)
            token = str(uuid.uuid4())[:8]
            ver_link = f"https://www.therestingfox.com/verification?token={token}"
            message = f"Please verify your email address by following this link: {ver_link}"
            subject = "Email Verification"
            emailing(email, subject, message, img=None)
            email_admin = os.getenv('EMAIL')
            subject_admin = "New user"
            message_admin = f"New user {username} has just registered."
            emailing(email_admin, subject_admin, message_admin, img=None)
            new_user = User(username=username, hash=hash, email=email, validation=token)
            db.session.add(new_user)
            db.session.commit()

            return redirect("/login")
        else:
            return render_template("register.html")
        
@app.route('/verification')
def verification():
    token = request.args.get('token')
    query = text("SELECT id FROM users WHERE validation = :token")
    check = db.session.execute(query, {'token': token}).fetchall()

    if not check:
        flash("Invalid token")
        return render_template("verify.html")    
    
    user_record = db.session.query(User).filter_by(validation=token).one_or_none()
    
    if user_record is None:
        flash("Invalid token", "error")
        return render_template("verify.html")
    
    # Update the user's validation status
    user_record.validation = 'Valid'
    db.session.commit()
    
    flash("Email verified successfully!")
    return render_template("login.html")

@app.route('/verify', methods=["GET", "POST"])
def verify():
    if request.method == "GET":
        user = session.get("user")
        return render_template("verify.html", user=user)
    else:
        user = session.get("user")
        user_record = db.session.query(User).filter_by(username=user).one_or_none()
        if not user_record:
            flash("User not found.", "error")
            return redirect("/login")
        email = user_record.email
        token = str(uuid.uuid4())[:8]
        ver_link = f"https://www.therestingfox.com/verify?token={token}"        
        subject = "Verification"
        message = f"Please verify your email address by following this link: {ver_link}"
        emailing(email, subject, message, img=None)
        user_record.validation = token
        db.session.commit()

        flash("Verification sent")
        return redirect("/verify")
      
@app.route("/pass_change", methods=["GET", "POST"])
def pass_change():
    if 'user_id' in session:
        user = session.get("user")
        if request.method == "POST":
            username = request.form.get("username")
            oldpass = request.form.get("password")
            newpass = request.form.get("newpass")
            confirmation = request.form.get("confirmation")

            if not username:
                flash("must provide username 403")
                return render_template("pass_change.html", admin=session.get('admin', False))
            if not oldpass:
                flash("must provide password 403")
                return render_template("pass_change.html", admin=session.get('admin', False))
            user_record = db.session.query(User).filter(User.username == username).one_or_none()
            if user_record is None:
                flash("No user found", "error")
                return render_template("pass_change.html", admin=session.get('admin', False))


            if not check_password_hash(user_record.hash, oldpass):
                flash("Invalid current password", "error")
                return render_template("pass_change.html", admin=session.get('admin', False))
            
            if not newpass:
                flash("Please enter the new password", "error")
                return render_template("pass_change.html", admin=session.get('admin', False))
            
            if newpass != confirmation:
                flash("New passwords don't match", "error")
                return render_template("pass_change.html", admin=session.get('admin', False))
            
            if newpass == oldpass:
                flash("New password cannot be the same as the current password", "error")
                return render_template("pass_change.html", admin=session.get('admin', False))

            # Update the password
            hashed_newpass = generate_password_hash(newpass)
            user_record.hash = hashed_newpass
            db.session.commit()

            flash("Password updated successfully", "success")
            return redirect("/login")
        else:
            return render_template("pass_change.html", admin=session.get('admin', False), user=user)
    else:
        return redirect("/login")

@app.route("/contact", methods=["GET", "POST"])
def contact():
        if request.method == "GET":
            if 'user_id' in session:
                user = session.get("user")
                return render_template("contact.html", admin=session.get('admin', False), user=user)
            else:
                return render_template("contact.html", admin=session.get('admin', False))
        else: 
            name = request.form.get("name")
            if not name:
                flash("Please enter your name/ username")
                return redirect("/contact")
            if 'user_id' in session:
                user = session.get("user")
                user_record = db.session.query(User.email).filter(User.username == user).scalar()
                if user_record:
                    user_email = user_record
                else:
                    flash("User email not found.")
                    return redirect("/contact")    
            else:
                user_email = request.form.get("user_email")
                if not user_email:
                    flash("Please enter your email you wish to be contacted on")
                    return redirect("/contact")                
            subject = request.form.get("subject")
            if not subject:
                flash("Please enter subject")
                return redirect("/contact")                
            message = request.form.get("message")
            if not message:
                flash("Please enter a message")
                return redirect("/contact")
            final_message = f"{name} has sent you a question: \n\n '{message}' \n\n They can be contacted on: {user_email}"
            email = os.getenv('EMAIL')
            emailing(email, subject, final_message, img=None)
            if 'user_id' in session: 
                return render_template("/sent.html", admin=session.get('admin', False), user=user)
            else:
                return render_template("/sent.html", admin=session.get('admin', False))

@app.route("/about", methods=["GET", "POST"])
def about():
    if request.method == "GET":
        if 'user_id' in session:
                user = session.get("user")
                return render_template("about.html", admin=session.get('admin', False), user=user)
        else:
            return render_template("about.html", admin=session.get('admin', False))

@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    day1 = Schedule.query.filter_by(date=27).order_by(Schedule.time).all()
    day2 = Schedule.query.filter_by(date=28).order_by(Schedule.time).all()
    day3 = Schedule.query.filter_by(date=29).order_by(Schedule.time).all()
    date = db.session.query(Schedule.date).group_by(Schedule.date).order_by(Schedule.date).all()
    time_req = request.form.get("time")
    date_req = request.form.get("date")

    if request.method == "GET":
        if 'user_id' in session:
            user = session.get("user")
            booking = Schedule.query.filter_by(user=user).order_by(Schedule.id).all()
            if not booking:
                return render_template("/schedule.html", admin=session.get('admin', False), day1=day1, day2=day2, day3=day3, date=date, user=user)
            else:
                booked = Schedule.query.filter_by(user=user).with_entities(Schedule.date, Schedule.time).all()
                return render_template("/schedule.html", admin=session.get('admin', False), day1=day1, day2=day2, day3=day3, date=date, booking=booking, booked=booked, user=user)        
        else:
            return render_template("/schedule.html", admin=session.get('admin', False), day1=day1, day2=day2, day3=day3, date=date)     
    else:
        if 'user_id' in session:
            user = session.get("user")
            booking = Schedule.query.filter_by(user=user).order_by(Schedule.id).all()
            result = db.session.execute(text("SELECT validation FROM users WHERE username = :username"), {'username': user}).scalar()
            if not result or result != 'Valid':
                flash("In order to book a time slot, please verify your email")
                return redirect("/verify")
            name = request.form.get("name")
            if name == "" or time_req == 'Time' or date_req == 'Date':
                if name == "":
                    flash("Please enter your name.")
                if time_req == 'Time':
                    flash("Please choose a time slot.")
                if date_req == 'Date':
                    flash("Please choose the date.")
                return render_template("schedule.html", admin=session.get('admin', False),  day1=day1, day2=day2, day3=day3, date=date)
            
            if not booking or session.get('admin'):
                schedule_entry = Schedule.query.filter_by(date=date_req, time=time_req).first()
                if schedule_entry:
                    schedule_entry.availability = 'Occupied'
                    schedule_entry.booked = name
                    schedule_entry.user = user
                    db.session.commit()

                return redirect ("/schedule")
            else:
                return render_template("schedule.html", admin=session.get('admin', False), day1=day1, day2=day2, day3=day3)
        else:
            return redirect("/login")   
         
@app.route("/cancel", methods = ["POST"])
def cancel():
    if 'user_id' in session:
        user = session.get("user")
        
        # Retrieve the schedule records for the logged-in user
        registrations = db.session.query(Schedule).filter_by(user=user).all()
        
        if registrations:
            # Assuming you want to cancel the first booking
            first_registration = registrations[0]
            first_registration.availability = 'Available'
            first_registration.booked = "None"
            first_registration.user = "None"
            
            db.session.commit()
            flash("Booking cancelled successfully.")
        else:
            flash("No bookings found to cancel.")
        
        return redirect("/schedule")
    else:
        flash("Please log in to cancel a booking.")
        return redirect("/login")

@app.route("/gift", methods=["GET", "POST"])
def gift():
    if 'user_id' in session:
        user = session.get("user")
        if request.method == "GET":
            giftcode = db.session.query(Gift.code, Gift.status).filter(Gift.username == user).all()
            return render_template ("/gift.html", admin=session.get('admin', False), giftcode=giftcode, user=user)
        else:
            result = db.session.query(User.validation).filter(User.username == user).scalar()
            if not result or result != 'Valid':
                flash("In order to request a giftcard, please verify your email")
                return redirect("/verify")
            giftcode = str(uuid.uuid4())[:8]
            to = request.form.get("to")
            if to == "":
                flash("Please enter a name")
                return redirect("/gift")
            gifter = request.form.get("from")
            if gifter == "":
                flash("Please enter who the gift is from")
                return redirect("/gift")
            duration = request.form.get("duration")
            gift_message = request.form.get("message") + f"This card grants you one session ({duration})."
            card(giftcode, gifter, to, gift_message)

            image_path3 = os.path.join('static', 'images', 'giftcard.jpg')
            with open(image_path3, 'rb') as file:    
                img = MIMEImage(file.read())
            
            user_email = db.session.query(User.email).filter(User.username == user).scalar()
            if user_email:
                email = user_email
                subject = "Copy of the giftcard"
                text = (
                    f"Hello {user},\n\n"
                    "Here is your requested giftcard. In order for the system to validate it, "
                    "contact us to discuss payment. For security reasons, we choose not to process "
                    "payments on this website. Once payment is received, we'll validate the giftcard "
                    "and notify you. If you have any questions, feel free to contact us at "
                    "restingfoxmassage@gmail.com.\n\nSincerely,\nDaniel"
                )
                emailing(email, subject, text, img)

                # Notify admin
                admin_email = os.getenv('EMAIL')
                admin_subject = "New giftcard request"
                admin_text = (
                    f"{user} has requested a giftcard: {giftcode} with the duration {duration}. "
                    f"They can be contacted at {email}"
                )
                emailing(admin_email, admin_subject, admin_text, img=None)
            new_gift = Gift(
                username=user,
                code=giftcode,
                status='Not Claimed',
                validation='Not Valid',
                duration=duration
            )
            db.session.add(new_gift)
            db.session.commit()
            return render_template ("/gift.html", admin=session.get('admin', False), is_post=True, img_path=image_path3, user=user)
    else:
        flash("Please login to request a giftcode")
        return redirect("/login")

def card(giftcode, gifter, to, gift_message):
    image_path = os.path.join('static', 'images', 'foxfox.jpg')
    img = Image.open(image_path)
    d = ImageDraw.Draw(img)
    
    giftcode_font = ImageFont.load_default(50)
    gifter_font = ImageFont.load_default(20)
    to_font = ImageFont.load_default(20)
    message_font = ImageFont.load_default(20)

    max_width = 600
    wrapped_text = wrap_text(gift_message, message_font, max_width, d)
    y_position = 430
    for line in wrapped_text:
        d.text((50, y_position), line, fill=(0, 0, 0), font=message_font)
        y_position += d.textbbox((0, 0), line, font=message_font)[3]

    d.text((385,275), f"{giftcode}", fill=(0, 0, 0), font=giftcode_font)
    d.text((97,373), f"{gifter}", fill=(0, 0, 0), font=gifter_font)
    d.text((70,347), f"{to}", fill=(0, 0, 0), font=to_font)

    image_path2 = os.path.join('static', 'images', 'giftcard.jpg')
    img = img.save(image_path2)

def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def emailing(email, subject, text, img):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL')
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(text, 'plain'))
    if img:
        msg.attach(img)
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], os.getenv('PASSWORD'))
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

@app.route('/get_times', methods=['POST'])
def get_times():
    times = [row[0] for row in db.session.execute(
        text("SELECT time FROM schedule WHERE availability = 'Available' AND date = :date ORDER BY time ASC"),
        {'date': request.json['date']}
    ).fetchall()]
    
    return jsonify(times)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    user = session.get("user")
    if 'user_id' in session and session.get('admin'):
        giftcodes_list = db.session.execute(text("SELECT * FROM gifts")).fetchall()
        user_list = db.session.execute(text("SELECT username, date, email, validation FROM users")).fetchall()
        return render_template("admin.html", admin=session.get('admin', False), giftcodes_list=giftcodes_list, user_list=user_list, user=user)
    else:
        return redirect("/login")
    
@app.route ("/questionaire", methods=["GET", "POST"])
def questionaire():
    if request.method == "GET":
        return render_template("questionaire.html", admin=session.get('admin', False))

@app.route ("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html", admin=session.get('admin', False))
    else:
        email = request.form.get("email")
        details = db.session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {'email': email}
        ).fetchone()

        if not details:
            flash("No account found with this email address.")
            return render_template("forgot.html")
        
        token = str(uuid.uuid4())[:8]
        db.session.execute(
            text("UPDATE users SET reset = :token, timestamp = CURRENT_TIMESTAMP WHERE email = :email"),
            {'token': token, 'email': email}
        )
        db.session.commit()


        ver_link = f"https://www.therestingfox.com/reset?token={token}"
        subject = "Password Reset"
        message = f"To reset your password - follow this link: {ver_link}"
        emailing(email, subject, message, img=None) 
        flash ("Email sent. Check your inbox")       
        return render_template("forgot.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "GET":
        token = request.args.get('token')
        if not token:
            flash("Invalid or missing token")
            return redirect("/forgot")

        # Check if the token is valid and not expired
        check = db.session.execute(
            text("SELECT id FROM users WHERE reset = :token AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'"),
            {'token': token}
        ).fetchone()

        if not check:
            flash("Invalid or expired token")
            return redirect("/forgot")

        return render_template("reset.html", token=token)

    else:
        token = request.form.get('token')
        newpass = request.form.get("newpass")
        confirmation = request.form.get("confirmation")

        if not newpass:
            flash("Please enter the new password")
            return render_template("reset.html", token=token)

        if newpass != confirmation:
            flash("New passwords don't match")
            return render_template("reset.html", token=token)

        # Fetch the current password hash for validation
        oldpass_hash = db.session.execute(
            text("SELECT hash FROM users WHERE reset = :token"),
            {'token': token}
        ).fetchone()

        if oldpass_hash:
            oldpass_hash = oldpass_hash[0]  # Access the first element directly
            if check_password_hash(oldpass_hash, newpass):
                flash("New password is the same as the old one. Choose a different password.")
                return render_template("reset.html", token=token)
        else:
            flash("No user found for the given token")
            return render_template("reset.html", token=token)

        # Hash the new password and update the user record
        newpass_hash = generate_password_hash(newpass)
        db.session.execute(
            text("UPDATE users SET hash = :newpass, reset = NULL, timestamp = NULL WHERE reset = :token"),
            {'newpass': newpass_hash, 'token': token}
        )
        db.session.commit()

        flash("Password changed successfully")
        return redirect("/login")

@app.route("/actions", methods=["GET", "POST"])
def actions():
    if request.method == "POST":
        action = request.form['action']
        if action == "claim":
            gift_id = request.form.get("id")
            gift = db.session.query(Gift).filter(Gift.id == gift_id).first()
            if gift.status == 'Not Claimed':
                gift.status = 'Claimed'
            else:
                gift.status = 'Not Claimed'
            db.session.commit()
        elif action == "validate":
            gift_id = request.form.get("id")
            gift = db.session.query(Gift).filter(Gift.id == gift_id).first()
            if gift.validation == 'Not Valid':
                gift.validation = 'Paid'
            else:
                gift.validation = 'Not Valid'
            db.session.commit()
        elif action == "delete":
            gift_id = request.form.get("id")
            gift = db.session.query(Gift).filter(Gift.id == gift_id).first()
            db.session.delete(gift)
            db.session.commit()
        elif action == "search":
            giftcode = request.form.get("giftcode").strip()
            if not giftcode:
                flash("Please enter a gift code.", "error")
                return redirect("/admin")  # Redirect to the admin page or appropriate page
            gifts = db.session.query(Gift).filter(Gift.code == giftcode).all()
            if not gifts:
                flash("No matching gift code found.", "error")
            giftcodes_list = db.session.query(Gift).all()
            return render_template("admin.html", admin=session.get('admin', False), giftcodes_list=giftcodes_list, search_results=gifts)
        elif action == "delete_user":
            user = request.form.get("username")
            # Use named placeholders for compatibility
            db.session.execute(text("DELETE FROM users WHERE username = :username"), {'username': user})
            db.session.commit()
            flash("User deleted successfully!")
        elif action == "validate_user":
            user = request.form.get("username")
            check = db.session.execute(text("SELECT id FROM users WHERE username = :username"), {"username": user}).scalar()
            if not check:
                flash("No user found.", "error")
            db.session.execute(text("UPDATE users SET validation = 'Valid' WHERE username = :username"), {"username": user})
            db.session.commit()      
        elif action == "mk_adm":
            user = request.form.get("username")
            check = db.session.execute(text("SELECT id FROM users WHERE username = :username"), {"username": user}).scalar()
            if not check:
                flash("No user found.", "error")
            db.session.execute(text("UPDATE users SET admin = 'TRUE' WHERE username = :username"), {"username": user})
            db.session.commit()
        elif action == "clear":
            booking_id = request.form.get("id")
            db.session.execute(text("UPDATE schedule SET availability = 'Available', booked = 'None', \"user\" = 'None' WHERE id = :id"), {'id': booking_id})
            db.session.commit()
            return redirect ("/schedule")
        elif action == "email_all":
            email_list = db.session.query(User.username, User.email).all()
            subject = request.form.get("subject")
            message_template = request.form.get("message")
            for user in email_list:
                message = f"Hello {user.username},\n\n{message_template}"
                emailing(user.email, subject, message, img=None)
            flash("Emails sent")
            return redirect ("/admin") 
    return redirect ("/admin")           

# added for heroku
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
