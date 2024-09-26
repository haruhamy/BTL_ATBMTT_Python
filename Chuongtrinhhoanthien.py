import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from random import randint
import zipfile


# Kiểm tra số nguyên tố
def is_prime(p):
    if p < 2:
        return False
    for i in range(2, int(p ** 0.5) + 1):
        if p % i == 0:
            return False
    return True


# Sinh ngẫu nhiên số nguyên tố
def random_primes():
    while True:
        p = randint(50, 100)
        if is_prime(p):
            break
    while True:
        g = randint(20, 50)
        if is_prime(g):
            break
    return p, g


# Hàm mã hóa / giải mã
def generator(g, x, p):
    return pow(g, x) % p


def encrypt_directory():
    text_key = entry_encrypt_key.get()
    if not text_key:
        messagebox.showerror("Error", "Please enter an encryption key")
        return
    
    dir_path = filedialog.askdirectory()
    if not dir_path:
        return

    # Hiện thông báo hỏi người dùng có chắc chắn muốn mã hóa không
    confirm = messagebox.askyesno("Confirm Encryption", f"Are you sure you want to encrypt the folder: {dir_path}?")
    if not confirm:
        return  # Nếu người dùng chọn "No", dừng quá trình mã hóa

    output_file = filedialog.asksaveasfilename(defaultextension=".encrypted", filetypes=[("Encrypted Files", "*.encrypted")])
    if not output_file:
        return

    p, g = random_primes()
    a = randint(p - 10, p)
    b = randint(g - 10, g)

    u = generator(g, a, p)
    v = generator(g, b, p)
    key = generator(v, a, p)
    b_key = generator(u, b, p)

    if key == b_key:
        shared_key = key
        
        # Tạo file zip trong bộ nhớ và mã hóa nó
        with zipfile.ZipFile('temp.zip', 'w') as zipf:
            for root, dirs, files in os.walk(dir_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    zipf.write(file_path, os.path.relpath(file_path, dir_path))

        with open('temp.zip', 'rb') as file:
            content = file.read()

        encrypted_message = bytearray()
        for i, byte in enumerate(content):
            key_char = ord(text_key[i % len(text_key)])  # Lấy byte từ text_key
            encrypted_byte = byte ^ key_char  # XOR với key
            encrypted_message.append(encrypted_byte)

        with open(output_file, 'wb') as enc_file:
            enc_file.write(encrypted_message)

        os.remove('temp.zip')  # Xóa file tạm sau khi mã hóa

        messagebox.showinfo("Success", "Directory encrypted successfully!")

        # Hiển thị thông tin mã hóa
        info = f"p: {p}, g: {g}, a: {a}, b: {b}, text_key: {text_key}"
        text_encrypt_info.delete(1.0, tk.END)
        text_encrypt_info.insert(tk.END, info)
    else:
        messagebox.showerror("Error", "Key mismatch")


def decrypt_directory():
    text_key = entry_decrypt_key.get()
    if not text_key:
        messagebox.showerror("Error", "Please enter a decryption key")
        return

    encrypted_file = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.encrypted")])
    if not encrypted_file:
        return

    output_dir = filedialog.askdirectory()
    if not output_dir:
        return

    a = int(entry_a.get())
    b = int(entry_b.get())
    
    u = generator(29, a, 53)
    v = generator(29, b, 53)
    key = generator(v, a, 53)
    b_key = generator(u, b, 53)

    if key == b_key:
        with open(encrypted_file, 'rb') as file:
            encrypted_content = file.read()

        decrypted_message = bytearray()
        for i, byte in enumerate(encrypted_content):
            key_char = ord(text_key[i % len(text_key)])  # Lấy byte từ text_key
            decrypted_byte = byte ^ key_char  # XOR với key
            decrypted_message.append(decrypted_byte)

        with open('temp_decrypted.zip', 'wb') as dec_file:
            dec_file.write(decrypted_message)

        # Giải nén tệp zip đã giải mã vào thư mục đầu ra
        with zipfile.ZipFile('temp_decrypted.zip', 'r') as zipf:
            zipf.extractall(output_dir)

        os.remove('temp_decrypted.zip')  # Xóa file tạm sau khi giải mã

        messagebox.showinfo("Success", "Directory decrypted successfully!")
    else:
        messagebox.showerror("Error", "Key mismatch")


# Tạo giao diện chính
root = tk.Tk()
root.title("Encryptor/Decryptor")
root.geometry("600x400")

# Tạo Notebook (Tab)
tab_control = ttk.Notebook(root)

# Tạo các tab mã hóa và giải mã
tab_encrypt = ttk.Frame(tab_control)
tab_decrypt = ttk.Frame(tab_control)

tab_control.add(tab_encrypt, text="Encrypt")
tab_control.add(tab_decrypt, text="Decrypt")

# Giao diện cho Tab Encrypt (Mã hóa)
ttk.Label(tab_encrypt, text="Enter Encryption Key:").pack(pady=10)
entry_encrypt_key = ttk.Entry(tab_encrypt, width=40)
entry_encrypt_key.pack(pady=5)

btn_encrypt = ttk.Button(tab_encrypt, text="Encrypt Directory", command=encrypt_directory)
btn_encrypt.pack(pady=20)

ttk.Label(tab_encrypt, text="Encryption Info:").pack(pady=10)
text_encrypt_info = tk.Text(tab_encrypt, height=5, width=60)
text_encrypt_info.pack(pady=10)

# Giao diện cho Tab Decrypt (Giải mã)
ttk.Label(tab_decrypt, text="Enter Decryption Key:").pack(pady=10)
entry_decrypt_key = ttk.Entry(tab_decrypt, width=40)
entry_decrypt_key.pack(pady=5)

ttk.Label(tab_decrypt, text="Enter value for a:").pack(pady=5)
entry_a = ttk.Entry(tab_decrypt, width=20)
entry_a.pack(pady=5)

ttk.Label(tab_decrypt, text="Enter value for b:").pack(pady=5)
entry_b = ttk.Entry(tab_decrypt, width=20)
entry_b.pack(pady=5)

btn_decrypt = ttk.Button(tab_decrypt, text="Decrypt Directory", command=decrypt_directory)
btn_decrypt.pack(pady=20)

# Thêm các tab vào giao diện
tab_control.pack(expand=1, fill="both")

root.mainloop()
