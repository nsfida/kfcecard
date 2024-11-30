from flask import Flask, render_template, request, send_file, redirect, url_for, session
from PIL import Image, ImageDraw, ImageFont
import os
import qrcode
import io
import base64

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key_here'

# Define paths for resources
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "static", "images", "logo.png")
LOGO1_PATH = os.path.join(BASE_DIR, "static", "images", "logo1.png")
LOGO2_PATH = os.path.join(BASE_DIR, "static", "images", "logo2.png")
SIGNATURE_PATH = os.path.join(BASE_DIR, "static", "images", "signature.png")
STAMP_PATH = os.path.join(BASE_DIR, "static", "images", "stamp.png")

# QR Code link
QR_CODE_URL = "wa.me/971568039690"

# Login credentials
USERS = {
    "nsfida": "746210",
    "ahmadaman": "456456",
    "sabirali": "356425",
    "arbabrizwan": "023663",
    "naveedali": "101081"
}

@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is already logged in
    if 'username' in session:
        return redirect(url_for('index'))

    # Load the logo and convert to base64 for the login page
    logo = Image.open(LOGO_PATH)
    logo_io = io.BytesIO()
    logo.save(logo_io, format="PNG", optimize=True)
    logo_base64 = base64.b64encode(logo_io.getvalue()).decode("utf-8")

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        if USERS.get(username) == password:
            # Successful login, store username in session
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # Incorrect login credentials
            error = "Invalid username or password"
            return render_template('login.html', error=error, logo_base64=logo_base64)

    return render_template('login.html', logo_base64=logo_base64)

@app.route("/")
def index():
    # Ensure user is logged in before accessing index
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_card():
    # Collect form data as before
    name = request.form["name"]
    urdu_name = request.form["urdu_name"]
    card_number = request.form["card_number"]
    designation = request.form["designation"]
    blood_group = request.form["blood_group"]
    contact = request.form["contact"]
    issuance_authority = request.form["issuance_authority"]

    # Check and handle uploaded photo
    uploaded_photo = request.files.get("photo")
    if not uploaded_photo:
        return "No photo uploaded. Please upload a photo.", 400

    # Load and process photo without degrading quality
    user_photo = Image.open(uploaded_photo)
    photo_io = io.BytesIO()
    user_photo.save(photo_io, format="PNG", optimize=True)
    photo_base64 = base64.b64encode(photo_io.getvalue()).decode("utf-8")

    # Load the main logo and keep its quality high
    logo = Image.open(LOGO_PATH)
    logo_io = io.BytesIO()
    logo.save(logo_io, format="PNG", optimize=True)
    logo_base64 = base64.b64encode(logo_io.getvalue()).decode("utf-8")

    # Load logo1 and logo2 for the left corners
    logo1 = Image.open(LOGO1_PATH)
    logo1_io = io.BytesIO()
    logo1.save(logo1_io, format="PNG", optimize=True)
    logo1_base64 = base64.b64encode(logo1_io.getvalue()).decode("utf-8")

    logo2 = Image.open(LOGO2_PATH)
    logo2_io = io.BytesIO()
    logo2.save(logo2_io, format="PNG", optimize=True)
    logo2_base64 = base64.b64encode(logo2_io.getvalue()).decode("utf-8")

    # Create a QR code and convert to base64
    qr = qrcode.QRCode(box_size=10, border=1)
    qr.add_data(QR_CODE_URL)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")
    qr_io = io.BytesIO()
    qr_img.save(qr_io, format="PNG")
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode("utf-8")

    # Load the signature and convert to base64
    signature = Image.open(SIGNATURE_PATH)
    signature_io = io.BytesIO()
    signature.save(signature_io, format="PNG", optimize=True)
    signature_base64 = base64.b64encode(signature_io.getvalue()).decode("utf-8")

    # Load the stamp and keep its quality high
    stamp = Image.open(STAMP_PATH)
    stamp_io = io.BytesIO()
    stamp.save(stamp_io, format="PNG", optimize=True)
    stamp_base64 = base64.b64encode(stamp_io.getvalue()).decode("utf-8")

    # Render all components to the HTML page
    return render_template(
        "generate.html",
        name=name,
        urdu_name=urdu_name,
        card_number=card_number,
        designation=designation,
        blood_group=blood_group,
        contact=contact,
        issuance_authority=issuance_authority,
        photo_base64=photo_base64,
        qr_base64=qr_base64,
        logo_base64=logo_base64,
        logo1_base64=logo1_base64,
        logo2_base64=logo2_base64,
        signature_base64=signature_base64,
        stamp_base64=stamp_base64,
    )

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    # Extract necessary data from the request
    name = request.form["name"]
    ecard_html = request.form["ecard_html"]

    # Generate PDF using the HTML content
    from xhtml2pdf import pisa
    pdf_io = io.BytesIO()
    pisa.CreatePDF(io.StringIO(ecard_html), dest=pdf_io)
    pdf_io.seek(0)

    # Serve the PDF as a downloadable file
    return send_file(pdf_io, as_attachment=True, download_name=f"{name}.pdf")

if __name__ == "__main__":
    app.run(debug=True)
