# 📋 ProgramTrack - Program Distribution Tracking System

A simple and efficient system for managing item distribution and acknowledgment. Track users who received items, capture their signatures, and automatically generate PDF receipts.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

- ✅ Full Arabic UI support (RTL)
- ✅ Manage multiple programs
- ✅ Electronic signature capture
- ✅ Automatic PDF receipt generation
- ✅ Import users from CSV files
- ✅ Compatible with tablets and phones
- ✅ Touch signature support on iPad
- ✅ Hide/show completed programs

## 📦 Requirements

- Python 3.8 or newer
- pip (Python package manager)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/meshawi/ProgramTrack.git
cd ProgramTrack
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

### 4. Open in browser

```
http://localhost:5000
```

## 📱 Access from iPad or Phone (Same Network)

If your device (iPad/phone) is on the same WiFi network:

1. Find your computer's IP address:
   - Windows: Open CMD and type `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. Open browser on iPad/phone and enter:
   ```
   http://192.168.1.100:5000
   ```

## 🌐 Access from Anywhere using Tailscale

[Tailscale](https://tailscale.com) is a free and easy VPN solution that allows you to securely access the system from anywhere in the world.

### Setup Steps:

#### 1. Create a Tailscale Account
- Go to [tailscale.com](https://tailscale.com)
- Sign up for a free account (you can use Google or Microsoft)

#### 2. Install Tailscale on the Computer (Server)
- Download Tailscale from [tailscale.com/download](https://tailscale.com/download)
- Install and sign in
- You'll get a Tailscale IP address (e.g., `100.x.x.x`)

#### 3. Install Tailscale on iPad/iPhone
- Download Tailscale from the App Store
- Sign in with the same account

#### 4. Install Tailscale on Android
- Download Tailscale from Google Play
- Sign in with the same account

#### 5. Access the System
After running Tailscale on all devices:

1. Find the computer's Tailscale address:
   - Open Tailscale on the computer
   - Copy the address (e.g., `100.100.100.100`)

2. From iPad or phone, open browser and enter:
   ```
   http://100.100.100.100:5000
   ```

### 💡 Tailscale Tips:
- Tailscale is free for up to 100 devices
- Connection is encrypted and secure
- Works even if devices are on different networks
- No router configuration or port forwarding needed

## 📁 Project Structure

```
ProgramTrack/
├── app.py                      # Main application
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── static/
│   └── style.css              # Styles
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Home page
│   ├── verify.html            # Verification page
│   ├── acknowledgment.html    # Acknowledgment & signature page
│   ├── message.html           # Message page
│   ├── manage.html            # Program management
│   ├── add_program.html       # Add program
│   ├── edit_program.html      # Edit program
│   ├── view_pdfs.html         # View receipts
│   └── help.html              # User guide
└── programs/
    ├── system-programs.csv    # Programs list
    └── [program_name]/
        ├── [program_name]-users.csv  # Users list
        └── [national_id].pdf         # PDF receipts
```

## 📝 How to Use

### Adding a New Program
1. Go to "Program Management"
2. Click "Add New Program"
3. Enter the Arabic name (for display) and English name (for files)

### Adding Users
From the program edit page, you can:
- **Manual add:** Enter National ID and full name
- **Import CSV:** Upload a file with `NationalID` and `FullName` columns

### Recording Receipt
1. Select the program from the home page
2. Enter the beneficiary's National ID
3. Ask the beneficiary to sign
4. Click "Confirm Receipt"

## 📄 CSV Import Format

```csv
NationalID,FullName
1234567890,Ahmed Mohammed
9876543210,Sara Ali
```

The system also supports Arabic column names:
```csv
رقم الهوية,الاسم الكامل
1234567890,أحمد محمد
```

## 🔧 Advanced Configuration

### Change Port
Edit the last line in `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### Run in Production
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## 🐛 Troubleshooting

### Problem: Arabic characters appear corrupted in Excel
**Solution:** Open the CSV file in Notepad++ and change encoding to UTF-8-BOM

### Problem: Cannot access from iPad
**Solution:** 
1. Make sure firewall allows port 5000
2. Ensure devices are on the same network
3. Use Tailscale for secure remote access

### Problem: PDF downloads instead of displaying
**Solution:** This is a Chrome setting:
1. Go to `chrome://settings/content/pdfDocuments`
2. Select "Open PDFs in Chrome"

---

**Developed by:** [Mohammed Aleshawi](https://aleshawi.me) © 2025
