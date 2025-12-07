from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import csv
from datetime import datetime
import base64
from io import BytesIO
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
import codecs
import subprocess
import platform

app = Flask(__name__)
app.secret_key = 'programtrack_secret_key_2024'

PROGRAMS_DIR = os.path.join(os.path.dirname(__file__), 'programs')
SYSTEM_CSV = os.path.join(PROGRAMS_DIR, 'system-programs.csv')

# Register Arabic font (using a system font that supports Arabic)
try:
    pdfmetrics.registerFont(TTFont('Arabic', 'C:/Windows/Fonts/arial.ttf'))
    ARABIC_FONT = 'Arabic'
except:
    ARABIC_FONT = 'Helvetica'

def arabic_text(text):
    """Reshape Arabic text for proper PDF rendering"""
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

def ensure_system_csv():
    """Ensure system-programs.csv exists"""
    if not os.path.exists(PROGRAMS_DIR):
        os.makedirs(PROGRAMS_DIR)
    if not os.path.exists(SYSTEM_CSV):
        with open(SYSTEM_CSV, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['EnglishName', 'ArabicName', 'ShowInList'])
            writer.writeheader()

def get_all_programs():
    """Get all programs from system-programs.csv"""
    ensure_system_csv()
    programs = []
    with open(SYSTEM_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            programs.append(row)
    return programs

def get_visible_programs():
    """Get only visible programs for main page"""
    all_programs = get_all_programs()
    return [p for p in all_programs if p.get('ShowInList', '').lower() == 'true']

def get_program_info(english_name):
    """Get program info by English name"""
    programs = get_all_programs()
    for p in programs:
        if p.get('EnglishName', '').strip() == english_name.strip():
            return p
    return None

def save_programs(programs):
    """Save all programs to system-programs.csv"""
    with open(SYSTEM_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['EnglishName', 'ArabicName', 'ShowInList'])
        writer.writeheader()
        writer.writerows(programs)

def create_program_folder(english_name):
    """Create program folder and empty CSV"""
    program_dir = os.path.join(PROGRAMS_DIR, english_name)
    if not os.path.exists(program_dir):
        os.makedirs(program_dir)
    
    csv_path = os.path.join(program_dir, f"{english_name}-users.csv")
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['NationalID', 'FullName', 'HasReceived', 'DateReceived'])
            writer.writeheader()

def validate_english_name(name):
    """Validate English name (no spaces, only letters, numbers, underscore, hyphen)"""
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
    return bool(re.match(pattern, name))

def get_csv_path(program_name):
    """Get the CSV file path for a program"""
    program_dir = os.path.join(PROGRAMS_DIR, program_name)
    csv_file = f"{program_name}-users.csv"
    return os.path.join(program_dir, csv_file)

def read_users(program_name):
    """Read all users from program CSV"""
    csv_path = get_csv_path(program_name)
    users = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
    return users

def find_user(program_name, national_id):
    """Find a user by national ID"""
    users = read_users(program_name)
    for user in users:
        if user.get('NationalID', '').strip() == national_id.strip():
            return user
    return None

def update_user_received(program_name, national_id):
    """Update user's HasReceived status to true and set DateReceived"""
    csv_path = get_csv_path(program_name)
    users = read_users(program_name)
    
    for user in users:
        if user.get('NationalID', '').strip() == national_id.strip():
            user['HasReceived'] = 'true'
            user['DateReceived'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['NationalID', 'FullName', 'HasReceived', 'DateReceived']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)

def generate_pdf(program_name, national_id, full_name, signature_data):
    """Generate PDF receipt with acknowledgment and signature"""
    program_dir = os.path.join(PROGRAMS_DIR, program_name)
    pdf_path = os.path.join(program_dir, f"{national_id}.pdf")
    
    # Get Arabic name for display
    program_info = get_program_info(program_name)
    arabic_program_name = program_info.get('ArabicName', program_name) if program_info else program_name
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont(ARABIC_FONT, 24)
    c.drawCentredString(width/2, height - 80, arabic_text("إيصال استلام"))
    
    # Program name
    c.setFont(ARABIC_FONT, 16)
    c.drawCentredString(width/2, height - 120, arabic_text(f"البرنامج: {arabic_program_name}"))
    
    # Line separator
    c.line(50, height - 140, width - 50, height - 140)
    
    # User details (right-aligned for Arabic)
    c.setFont(ARABIC_FONT, 14)
    c.drawRightString(width - 50, height - 180, arabic_text(f"رقم الهوية: {national_id}"))
    c.drawRightString(width - 50, height - 210, arabic_text(f"الاسم الكامل: {full_name}"))
    c.drawRightString(width - 50, height - 240, arabic_text(f"تاريخ الاستلام: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
    
    # Acknowledgment text
    c.setFont(ARABIC_FONT, 12)
    c.drawRightString(width - 50, height - 290, arabic_text("إقرار بالاستلام:"))
    c.setFont(ARABIC_FONT, 11)
    acknowledgment_text = f"أقر أنا، {full_name}، بأنني قد استلمت المواد/الأغراض"
    c.drawRightString(width - 50, height - 315, arabic_text(acknowledgment_text))
    c.drawRightString(width - 50, height - 335, arabic_text(f"من {arabic_program_name}."))
    
    # Signature
    c.setFont(ARABIC_FONT, 12)
    c.drawRightString(width - 50, height - 390, arabic_text("التوقيع:"))
    
    # Add signature image with white background
    if signature_data and signature_data.startswith('data:image'):
        try:
            img_data = signature_data.split(',')[1]
            img_bytes = base64.b64decode(img_data)
            
            img = Image.open(BytesIO(img_bytes))
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            img_reader = ImageReader(img_buffer)
            c.drawImage(img_reader, width - 300, height - 550, width=250, height=120, preserveAspectRatio=True)
        except Exception as e:
            c.drawRightString(width - 50, height - 420, arabic_text("[التوقيع محفوظ]"))
    
    # Footer
    c.line(50, 80, width - 50, 80)
    c.setFont(ARABIC_FONT, 10)
    c.drawCentredString(width/2, 60, arabic_text("هذا إيصال رسمي"))
    c.drawCentredString(width/2, 45, arabic_text(f"تم الإنشاء بتاريخ {datetime.now().strftime('%Y-%m-%d')} الساعة {datetime.now().strftime('%H:%M:%S')}"))
    
    c.save()
    return pdf_path

def get_program_pdfs(english_name):
    """Get list of all PDFs for a program"""
    program_dir = os.path.join(PROGRAMS_DIR, english_name)
    pdfs = []
    if os.path.exists(program_dir):
        for file in os.listdir(program_dir):
            if file.endswith('.pdf'):
                national_id = file.replace('.pdf', '')
                # Try to find user name
                user = find_user(english_name, national_id)
                user_name = user.get('FullName', 'غير معروف') if user else 'غير معروف'
                
                # Get file modification time
                file_path = os.path.join(program_dir, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                pdfs.append({
                    'filename': file,
                    'national_id': national_id,
                    'user_name': user_name,
                    'date': mod_time.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # Sort by date (newest first)
    pdfs.sort(key=lambda x: x['date'], reverse=True)
    return pdfs

def add_user_to_program(program_name, national_id, full_name):
    """Add a new user to program CSV"""
    csv_path = get_csv_path(program_name)
    users = read_users(program_name)
    
    # Check if user already exists
    for user in users:
        if user.get('NationalID', '').strip() == national_id.strip():
            return False, "رقم الهوية موجود مسبقاً"
    
    # Add new user
    users.append({
        'NationalID': national_id,
        'FullName': full_name,
        'HasReceived': 'false',
        'DateReceived': ''
    })
    
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['NationalID', 'FullName', 'HasReceived', 'DateReceived']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)
    
    return True, "تم إضافة المستخدم بنجاح"

def import_users_from_csv(program_name, file_content):
    """Import users from uploaded CSV file"""
    csv_path = get_csv_path(program_name)
    existing_users = read_users(program_name)
    existing_ids = {user.get('NationalID', '').strip() for user in existing_users}
    
    imported_count = 0
    skipped_count = 0
    
    try:
        # Try different encodings
        try:
            content = file_content.decode('utf-8-sig')
        except:
            try:
                content = file_content.decode('utf-8')
            except:
                content = file_content.decode('latin-1')
        
        lines = content.strip().split('\n')
        
        # Parse CSV
        reader = csv.DictReader(lines)
        
        for row in reader:
            # Try different possible column names
            national_id = row.get('NationalID') or row.get('nationalid') or row.get('National ID') or row.get('رقم الهوية') or row.get('رقم_الهوية') or ''
            full_name = row.get('FullName') or row.get('fullname') or row.get('Full Name') or row.get('الاسم') or row.get('الاسم الكامل') or row.get('الاسم_الكامل') or ''
            
            national_id = str(national_id).strip()
            full_name = str(full_name).strip()
            
            if national_id and full_name:
                if national_id not in existing_ids:
                    existing_users.append({
                        'NationalID': national_id,
                        'FullName': full_name,
                        'HasReceived': 'false',
                        'DateReceived': ''
                    })
                    existing_ids.add(national_id)
                    imported_count += 1
                else:
                    skipped_count += 1
        
        # Save updated users
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['NationalID', 'FullName', 'HasReceived', 'DateReceived']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_users)
        
        return True, f"تم استيراد {imported_count} مستخدم. تم تخطي {skipped_count} (موجودين مسبقاً)"
    
    except Exception as e:
        return False, f"خطأ في استيراد الملف: {str(e)}"

def get_program_users_count(program_name):
    """Get count of users and received count for a program"""
    users = read_users(program_name)
    total = len(users)
    received = sum(1 for u in users if u.get('HasReceived', '').lower() == 'true')
    return total, received

@app.context_processor
def inject_now():
    """Inject current datetime into all templates"""
    return {'now': datetime.now()}

@app.route('/help')
def help_page():
    """Help and documentation page"""
    return render_template('help.html')

@app.route('/')
def index():
    """Home page - Program selection"""
    programs = get_visible_programs()
    return render_template('index.html', programs=programs)

@app.route('/manage')
def manage_programs():
    """Program management page"""
    programs = get_all_programs()
    return render_template('manage.html', programs=programs)

@app.route('/manage/add', methods=['GET', 'POST'])
def add_program():
    """Add new program"""
    if request.method == 'POST':
        english_name = request.form.get('english_name', '').strip().lower()
        arabic_name = request.form.get('arabic_name', '').strip()
        
        if not english_name or not arabic_name:
            flash('الرجاء إدخال جميع الحقول', 'error')
            return redirect(url_for('add_program'))
        
        if not validate_english_name(english_name):
            flash('الاسم الإنجليزي غير صالح. استخدم أحرف إنجليزية وأرقام وشرطات فقط، ويجب أن يبدأ بحرف', 'error')
            return redirect(url_for('add_program'))
        
        # Check if program already exists
        if get_program_info(english_name):
            flash('هذا البرنامج موجود مسبقاً', 'error')
            return redirect(url_for('add_program'))
        
        # Add to system CSV
        programs = get_all_programs()
        programs.append({
            'EnglishName': english_name,
            'ArabicName': arabic_name,
            'ShowInList': 'true'
        })
        save_programs(programs)
        
        # Create program folder and CSV
        create_program_folder(english_name)
        
        flash(f'تم إنشاء البرنامج "{arabic_name}" بنجاح', 'success')
        return redirect(url_for('manage_programs'))
    
    return render_template('add_program.html')

@app.route('/manage/toggle/<english_name>')
def toggle_program(english_name):
    """Toggle program visibility"""
    programs = get_all_programs()
    for p in programs:
        if p.get('EnglishName') == english_name:
            current = p.get('ShowInList', 'true').lower() == 'true'
            p['ShowInList'] = 'false' if current else 'true'
            break
    save_programs(programs)
    flash('تم تحديث حالة البرنامج', 'success')
    return redirect(url_for('manage_programs'))

@app.route('/manage/edit/<english_name>', methods=['GET', 'POST'])
def edit_program(english_name):
    """Edit program Arabic name and manage users"""
    program = get_program_info(english_name)
    if not program:
        flash('البرنامج غير موجود', 'error')
        return redirect(url_for('manage_programs'))
    
    if request.method == 'POST':
        action = request.form.get('action', 'update_name')
        
        if action == 'update_name':
            arabic_name = request.form.get('arabic_name', '').strip()
            if not arabic_name:
                flash('الرجاء إدخال الاسم العربي', 'error')
                return redirect(url_for('edit_program', english_name=english_name))
            
            programs = get_all_programs()
            for p in programs:
                if p.get('EnglishName') == english_name:
                    p['ArabicName'] = arabic_name
                    break
            save_programs(programs)
            flash('تم تحديث البرنامج بنجاح', 'success')
        
        elif action == 'add_user':
            national_id = request.form.get('national_id', '').strip()
            full_name = request.form.get('full_name', '').strip()
            
            if not national_id or not full_name:
                flash('الرجاء إدخال رقم الهوية والاسم الكامل', 'error')
            else:
                success, message = add_user_to_program(english_name, national_id, full_name)
                flash(message, 'success' if success else 'error')
        
        elif action == 'import_csv':
            if 'csv_file' not in request.files:
                flash('الرجاء اختيار ملف CSV', 'error')
            else:
                file = request.files['csv_file']
                if file.filename == '':
                    flash('الرجاء اختيار ملف CSV', 'error')
                elif not file.filename.endswith('.csv'):
                    flash('الرجاء اختيار ملف بصيغة CSV', 'error')
                else:
                    content = file.read()
                    success, message = import_users_from_csv(english_name, content)
                    flash(message, 'success' if success else 'error')
        
        return redirect(url_for('edit_program', english_name=english_name))
    
    # Get user stats
    total_users, received_users = get_program_users_count(english_name)
    csv_path = get_csv_path(english_name)
    
    return render_template('edit_program.html', 
                          program=program, 
                          total_users=total_users, 
                          received_users=received_users,
                          csv_path=csv_path)

@app.route('/manage/open-csv/<english_name>')
def open_csv_folder(english_name):
    """Open the CSV file location in file explorer"""
    program = get_program_info(english_name)
    if not program:
        flash('البرنامج غير موجود', 'error')
        return redirect(url_for('manage_programs'))
    
    csv_path = get_csv_path(english_name)
    folder_path = os.path.dirname(csv_path)
    
    try:
        if platform.system() == 'Windows':
            os.startfile(folder_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', folder_path])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])
        flash('تم فتح مجلد البرنامج', 'success')
    except Exception as e:
        flash(f'لا يمكن فتح المجلد: {str(e)}', 'error')
    
    return redirect(url_for('edit_program', english_name=english_name))

@app.route('/verify/<program_name>', methods=['GET', 'POST'])
def verify(program_name):
    """User verification page"""
    program_info = get_program_info(program_name)
    if not program_info:
        flash('البرنامج غير موجود', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        national_id = request.form.get('national_id', '').strip()
        
        if not national_id:
            flash('الرجاء إدخال رقم الهوية', 'error')
            return redirect(url_for('verify', program_name=program_name))
        
        user = find_user(program_name, national_id)
        
        if not user:
            message = f"المستخدم غير موجود. الرجاء إضافة رقم الهوية يدوياً في ملف {program_name}-users.csv"
            return render_template('message.html', message=message, message_type='error', program_name=program_name, program_info=program_info)
        
        if user.get('HasReceived', '').lower() == 'true':
            message = f"المستخدم {user.get('FullName', 'غير معروف')} قد استلم المواد مسبقاً بتاريخ {user.get('DateReceived', 'غير محدد')}."
            return render_template('message.html', message=message, message_type='warning', program_name=program_name, program_info=program_info)
        
        return redirect(url_for('acknowledgment', program_name=program_name, national_id=national_id))
    
    return render_template('verify.html', program_name=program_name, program_info=program_info)

@app.route('/acknowledgment/<program_name>/<national_id>', methods=['GET', 'POST'])
def acknowledgment(program_name, national_id):
    """Acknowledgment and signature page"""
    program_info = get_program_info(program_name)
    user = find_user(program_name, national_id)
    
    if not user:
        flash('المستخدم غير موجود', 'error')
        return redirect(url_for('verify', program_name=program_name))
    
    if request.method == 'POST':
        signature_data = request.form.get('signature', '')
        
        if not signature_data:
            flash('الرجاء إضافة توقيعك', 'error')
            return render_template('acknowledgment.html', user=user, program_name=program_name, program_info=program_info)
        
        update_user_received(program_name, national_id)
        generate_pdf(program_name, national_id, user.get('FullName', ''), signature_data)
        
        message = f"شكراً لك، {user.get('FullName')}! تم تسجيل الاستلام وإنشاء الإيصال بنجاح."
        return render_template('message.html', message=message, message_type='success', program_name=program_name, program_info=program_info)
    
    return render_template('acknowledgment.html', user=user, program_name=program_name, program_info=program_info)

@app.route('/manage/pdfs/<english_name>')
def view_pdfs(english_name):
    """View all PDFs for a program"""
    program_info = get_program_info(english_name)
    if not program_info:
        flash('البرنامج غير موجود', 'error')
        return redirect(url_for('manage_programs'))
    
    pdfs = get_program_pdfs(english_name)
    return render_template('view_pdfs.html', program_info=program_info, pdfs=pdfs, program_name=english_name)

@app.route('/manage/pdfs/<english_name>/download/<filename>')
def download_pdf(english_name, filename):
    """View a specific PDF in browser"""
    program_info = get_program_info(english_name)
    if not program_info:
        flash('البرنامج غير موجود', 'error')
        return redirect(url_for('manage_programs'))
    
    # Security check - ensure filename is safe
    if not filename.endswith('.pdf') or '/' in filename or '\\' in filename:
        flash('ملف غير صالح', 'error')
        return redirect(url_for('view_pdfs', english_name=english_name))
    
    file_path = os.path.join(PROGRAMS_DIR, english_name, filename)
    if not os.path.exists(file_path):
        flash('الملف غير موجود', 'error')
        return redirect(url_for('view_pdfs', english_name=english_name))
    
    # Send file with correct mimetype and inline disposition to view in browser
    return send_file(
        file_path, 
        mimetype='application/pdf',
        as_attachment=False,
        download_name=filename
    )

if __name__ == '__main__':
    ensure_system_csv()
    app.run(host='0.0.0.0', port=5000, debug=True)
