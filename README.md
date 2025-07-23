#  Advance File Encryption & Decryption Tool

A simple yet powerful tool to **encrypt and decrypt any file or folder** with a password.  
Protect your sensitive data from hackers, prying eyes, or accidental leaks — all with a user-friendly interface!

##  Features

- **AES (Fernet) & DES encryption** — bank-level security
- **Encrypt/Decrypt any file or folder**
- **Password & Re-type Password** (with Show/Hide)
- **Password strength indicator**
- **Password hint** (for recovery)
- **Progress bar** for large files
- **Dark/Light theme**
- **Owner name & website link in the footer**
- **No technical skills needed!**


##  Why Use This Tool?

- **Keep your files and passwords safe** — even if your computer is hacked, your encrypted files are unreadable without the password.
- **Easy to use** — no command line, just click and go.
- **Share files securely** — send encrypted files via email or cloud.
- **Works with multiple files and folders at once.**


##  Screenshots

*(Add your screenshots here)*


##  Installation

### 1. **Run the .exe (Windows)**

- Double-click to run.  
  No need to install Python or any libraries!

### 2. **Or, Run from Source (Any OS)**

1. Install Python 3.8+ (Recommended: 3.10 or 3.11)
2. Install dependencies:
    ```bash
    pip install cryptography pycryptodome ttkthemes pillow plyer
    ```
3. Download or clone this repo.
4. Run:
    ```bash
    python encryption-decryption.py
    ```


##  How to Use

1. **Add Files/Add Folder** — select files or folders to encrypt/decrypt.
2. **Choose Output Directory** — where the result will be saved.
3. **Enter Password & Re-type Password** — use Show/Hide to check.
4. **(Optional) Add a Password Hint** — for your memory.
5. **Select Algorithm** — AES (recommended) or DES.
6. **Click Encrypt or Decrypt** — progress bar and status will show.
7. **Done!** — check your output folder.


##  Security Tips

- Use a **strong password** (long, mixed, unique).
- **Never share your password** with anyone.
- Make your hint helpful for you, but not obvious for others.
- **Always use AES** for best security.
