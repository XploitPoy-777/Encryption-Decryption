import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, hashlib, shutil, csv, subprocess, sys
from ttkthemes import ThemedTk
from datetime import datetime

def file_hash(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates(folder, progress_callback=None):
    files_seen = {}
    duplicates = []
    all_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)
    total = len(all_files)
    for idx, full_path in enumerate(all_files):
        try:
            size = os.path.getsize(full_path)
            mtime = os.path.getmtime(full_path)
            key = (os.path.basename(full_path), size)
            if key in files_seen:
                # Same name & size, check hash
                if file_hash(full_path) == file_hash(files_seen[key][0]):
                    duplicates.append({
                        "duplicate": full_path,
                        "original": files_seen[key][0],
                        "size": size,
                        "mtime": mtime
                    })
            else:
                files_seen[key] = (full_path, mtime)
        except Exception as e:
            continue
        if progress_callback:
            percent = int((idx+1)/total*100) if total else 100
            progress_callback(idx+1, total, percent)
    return duplicates

def select_folder():
    folder = filedialog.askdirectory(title="Select Folder")
    if folder:
        folder_var.set(folder)

def scan_duplicates():
    folder = folder_var.get()
    if not folder:
        messagebox.showerror("Error", "Please select a folder!")
        return
    status_var.set("Scanning...")
    progress_bar['value'] = 0
    percent_label.config(text="0%")
    root.update()
    def update_progress(current, total, percent):
        progress_bar['maximum'] = total
        progress_bar['value'] = current
        percent_label.config(text=f"{percent}%")
        root.update_idletasks()
    global all_duplicates
    all_duplicates = find_duplicates(folder, update_progress)
    percent_label.config(text="100%")
    show_filtered_duplicates()
    status_var.set(f"Scan complete! {len(all_duplicates)} duplicate(s) found.")

def show_filtered_duplicates(*args):
    ext = ext_var.get().strip().lower()
    name = name_var.get().strip().lower()
    minsize = minsize_var.get().strip()
    filtered = []
    total_size = 0
    for dup in all_duplicates:
        fname = os.path.basename(dup["duplicate"]).lower()
        fext = os.path.splitext(fname)[1].lower()
        fsize = dup["size"]
        if ext and not fname.endswith(ext):
            continue
        if name and name not in fname:
            continue
        if minsize:
            try:
                if fsize < int(minsize)*1024:
                    continue
            except:
                pass
        filtered.append(dup)
        total_size += fsize
    for row in tree.get_children():
        tree.delete(row)
    for idx, dup in enumerate(filtered, 1):
        tree.insert("", "end", iid=idx, values=(
            idx,
            "",  # Checkbox column (blank initially)
            dup["duplicate"],
            dup["original"],
            f"{dup['size']//1024} KB",
            datetime.fromtimestamp(dup["mtime"]).strftime("%Y-%m-%d %H:%M")
        ))
    mb = total_size / (1024*1024)
    count_label.config(text=f"Total Duplicates: {len(filtered)}   |   Total Size: {mb:.2f} MB")
    if not filtered:
        status_var.set("No duplicates found with current filter.")

def toggle_select_all():
    checked = select_all_var.get()
    for row in tree.get_children():
        tree.set(row, "Select", "✔" if checked else "")

def on_tree_click(event):
    region = tree.identify("region", event.x, event.y)
    if region == "cell":
        col = tree.identify_column(event.x)
        if col == "#2":  # "Select" column
            row = tree.identify_row(event.y)
            if row:
                current = tree.set(row, "Select")
                tree.set(row, "Select", "" if current == "✔" else "✔")

def delete_selected():
    selected = [row for row in tree.get_children() if tree.set(row, "Select") == "✔"]
    if not selected:
        messagebox.showwarning("No Selection", "No duplicate files selected for deletion.")
        return
    if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected)} duplicate files?"):
        return
    for row in selected:
        try:
            os.remove(tree.set(row, "Duplicate"))
            tree.delete(row)
        except Exception as e:
            continue
    status_var.set(f"Deleted {len(selected)} files.")
    show_filtered_duplicates()

def move_selected():
    selected = [row for row in tree.get_children() if tree.set(row, "Select") == "✔"]
    if not selected:
        messagebox.showwarning("No Selection", "No duplicate files selected for moving.")
        return
    dest = filedialog.askdirectory(title="Select Destination Folder")
    if not dest:
        return
    for row in selected:
        try:
            shutil.move(tree.set(row, "Duplicate"), dest)
            tree.delete(row)
        except Exception as e:
            continue
    status_var.set(f"Moved {len(selected)} files.")
    show_filtered_duplicates()

def export_csv():
    if not tree.get_children():
        messagebox.showwarning("No Data", "No duplicate files to export.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not file:
        return
    with open(file, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SL", "Duplicate", "Original", "Size", "Modified"])
        for row in tree.get_children():
            writer.writerow([
                tree.set(row, "SL"),
                tree.set(row, "Duplicate"),
                tree.set(row, "Original"),
                tree.set(row, "Size"),
                tree.set(row, "Modified")
            ])
    messagebox.showinfo("Exported", f"Duplicate list exported to {file}")

def switch_theme(*args):
    root.set_theme("arc" if theme_var.get() == "Dark" else "plastik")

def open_file(event=None):
    selected = tree.focus()
    if not selected:
        return
    file_path = tree.set(selected, "Duplicate")
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "File does not exist!")
        return
    try:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', file_path))
        elif os.name == 'nt':
            os.startfile(file_path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', file_path))
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file:\n{e}")

def toggle_fullscreen():
    is_full = root.attributes('-fullscreen')
    root.attributes('-fullscreen', not is_full)

def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

# --- GUI ---
root = ThemedTk(theme="arc")
root.title("File Duplicate Finder")
root.geometry("1200x700")
root.resizable(True, True)

# Folder select
folder_var = tk.StringVar()
status_var = tk.StringVar(value="Ready")
theme_var = tk.StringVar(value="Dark")
all_duplicates = []

top_frame = ttk.Frame(root)
top_frame.pack(fill="x", padx=20, pady=10)

ttk.Label(top_frame, text="Select Folder:", font=("Segoe UI", 11)).pack(side="left")
ttk.Entry(top_frame, textvariable=folder_var, width=60).pack(side="left", padx=10)
ttk.Button(top_frame, text="Browse", command=select_folder).pack(side="left", padx=5)
ttk.Button(top_frame, text="Scan Duplicates", command=scan_duplicates).pack(side="left", padx=5)
ttk.Label(top_frame, text="Theme:").pack(side="left", padx=10)
theme_combo = ttk.Combobox(top_frame, textvariable=theme_var, values=["Dark", "Light"], width=8, state="readonly")
theme_combo.pack(side="left")
theme_var.trace("w", switch_theme)
ttk.Button(top_frame, text="Full Screen (F11)", command=toggle_fullscreen).pack(side="left", padx=10)

# Filter frame
filter_frame = ttk.LabelFrame(root, text="Filter Duplicates")
filter_frame.pack(fill="x", padx=20, pady=5)
ttk.Label(filter_frame, text="Extension (e.g. .jpg):").pack(side="left", padx=5)
ext_var = tk.StringVar()
ttk.Entry(filter_frame, textvariable=ext_var, width=10).pack(side="left", padx=5)
ttk.Label(filter_frame, text="Name contains:").pack(side="left", padx=5)
name_var = tk.StringVar()
ttk.Entry(filter_frame, textvariable=name_var, width=15).pack(side="left", padx=5)
ttk.Label(filter_frame, text="Min Size (KB):").pack(side="left", padx=5)
minsize_var = tk.StringVar()
ttk.Entry(filter_frame, textvariable=minsize_var, width=8).pack(side="left", padx=5)
ttk.Button(filter_frame, text="Apply Filter", command=show_filtered_duplicates).pack(side="left", padx=10)

# Treeview for results with Scrollbars
columns = ("SL", "Select", "Duplicate", "Original", "Size", "Modified")
tree_frame = ttk.Frame(root)
tree_frame.pack(fill="both", padx=20, pady=10, expand=True)

tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20,
                    yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)
tree_scroll_y.pack(side="right", fill="y")
tree_scroll_x.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

tree.heading("SL", text="SL No.")
tree.heading("Select", text="Select")
tree.heading("Duplicate", text="Duplicate File")
tree.heading("Original", text="Original File")
tree.heading("Size", text="Size")
tree.heading("Modified", text="Modified")

tree.column("SL", width=60, anchor="center")
tree.column("Select", width=60, anchor="center")
tree.column("Duplicate", width=350)
tree.column("Original", width=350)
tree.column("Size", width=80, anchor="center")
tree.column("Modified", width=120, anchor="center")

# Double click to open file
tree.bind("<Double-1>", open_file)
tree.bind("<Button-1>", on_tree_click)

# Checkbox for select all
select_all_var = tk.BooleanVar()
select_all_cb = ttk.Checkbutton(root, text="Select All", variable=select_all_var, command=toggle_select_all)
select_all_cb.pack(anchor="w", padx=25)

# Total count label
count_label = ttk.Label(root, text="Total Duplicates: 0   |   Total Size: 0.00 MB", font=("Segoe UI", 11, "bold"))
count_label.pack(anchor="center", pady=2)

# Action buttons
action_frame = ttk.Frame(root)
action_frame.pack(pady=10)
ttk.Button(action_frame, text="Delete Selected", command=delete_selected).pack(side="left", padx=10)
ttk.Button(action_frame, text="Move Selected", command=move_selected).pack(side="left", padx=10)
ttk.Button(action_frame, text="Export to CSV", command=export_csv).pack(side="left", padx=10)
ttk.Button(action_frame, text="Exit Full Screen (Esc)", command=exit_fullscreen).pack(side="left", padx=10)

# Progress bar and percent label
progress_frame = ttk.Frame(root)
progress_frame.pack(pady=(0, 5))
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=900, mode="determinate")
progress_bar.pack(side="left")
percent_label = ttk.Label(progress_frame, text="0%", font=("Segoe UI", 10, "bold"))
percent_label.pack(side="left", padx=10)

# Status bar
status_bar = ttk.Label(root, textvariable=status_var, anchor="w", relief="sunken", font=("Segoe UI", 10))
status_bar.pack(side="bottom", fill="x")

# Keyboard shortcut for full screen
root.bind("<F11>", lambda e: toggle_fullscreen())
root.bind("<Escape>", exit_fullscreen)

# Filter live update
ext_var.trace("w", show_filtered_duplicates)
name_var.trace("w", show_filtered_duplicates)
minsize_var.trace("w", show_filtered_duplicates)

root.mainloop()