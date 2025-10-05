import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import bcrypt
from datetime import datetime

class CabinetPediatrie:
    def __init__(self, root):
        self.root = root
        self.root.title("Cabinet Pédiatrique")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f8f9fa")

        self.db_conn = sqlite3.connect('consultations.db')
        self.create_tables()

        self.current_user = None
        self.show_login_screen()

    def create_tables(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_consultation TEXT NOT NULL,
                nom_patient TEXT NOT NULL,
                prenom_patient TEXT NOT NULL,
                age INTEGER NOT NULL,
                motif_consultation TEXT NOT NULL,
                examen_clinique TEXT,
                examens_complementaires TEXT,
                traitement TEXT
            )
        ''')
        # Insert default user if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'doctor'")
        if not cursor.fetchone():
            hashed_password = bcrypt.hashpw('doctor'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('doctor', hashed_password))
        self.db_conn.commit()

    def show_login_screen(self):
        self.clear_frame()

        login_frame = tk.Frame(self.root, bg="#667eea")
        login_frame.pack(expand=True, fill="both")

        login_card = tk.Frame(login_frame, bg="white", bd=5, relief="groove")
        login_card.place(relx=0.5, rely=0.5, anchor="center")

        header_label = tk.Label(login_card, text="Connexion", font=("Segoe UI", 24, "bold"), bg="white", fg="#333")
        header_label.pack(pady=(20, 10))

        username_label = tk.Label(login_card, text="Nom d'utilisateur", font=("Segoe UI", 12), bg="white")
        username_label.pack(pady=(10, 5))
        self.username_entry = ttk.Entry(login_card, font=("Segoe UI", 12))
        self.username_entry.pack(pady=5, padx=20)

        password_label = tk.Label(login_card, text="Mot de passe", font=("Segoe UI", 12), bg="white")
        password_label.pack(pady=(10, 5))
        self.password_entry = ttk.Entry(login_card, show="*", font=("Segoe UI", 12))
        self.password_entry.pack(pady=5, padx=20)

        login_button = ttk.Button(login_card, text="Se connecter", command=self.login, style="Accent.TButton")
        login_button.pack(pady=20, padx=20, fill="x")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get().encode('utf-8')

        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password, user[2]):
            self.current_user = user[1]
            self.show_dashboard()
        else:
            messagebox.showerror("Erreur de connexion", "Nom d'utilisateur ou mot de passe incorrect")

    def show_dashboard(self):
        self.clear_frame()

        header_frame = tk.Frame(self.root, bg="#667eea", height=70)
        header_frame.pack(fill="x")

        title_label = tk.Label(header_frame, text="Cabinet Pédiatrique", font=("Segoe UI", 24, "bold"), bg="#667eea", fg="white")
        title_label.pack(side="left", padx=20)
        
        logout_button = ttk.Button(header_frame, text="Déconnexion", command=self.show_login_screen, style="Accent.TButton")
        logout_button.pack(side="right", padx=20)
        
        welcome_label = tk.Label(header_frame, text=f"Bienvenue, Dr Taibi Houria", font=("Segoe UI", 12), bg="#667eea", fg="white")
        welcome_label.pack(side="right")

        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(expand=True, fill="both")

        sidebar = tk.Frame(main_frame, bg="white", width=250, bd=2, relief="groove")
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.content_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
        self.content_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Sidebar buttons
        consultations_button = ttk.Button(sidebar, text="Consultations", command=self.show_consultations_view, style="Nav.TButton")
        consultations_button.pack(fill="x", pady=10, padx=10)
        
        new_consultation_button = ttk.Button(sidebar, text="Nouvelle Consultation", command=self.show_new_consultation_view, style="Nav.TButton")
        new_consultation_button.pack(fill="x", pady=10, padx=10)

        stats_button = ttk.Button(sidebar, text="Statistiques", command=self.show_stats_view, style="Nav.TButton")
        stats_button.pack(fill="x", pady=10, padx=10)

        self.show_consultations_view()

    def show_consultations_view(self):
        self.clear_content_frame()
        
        title_label = tk.Label(self.content_frame, text="Liste des Consultations", font=("Segoe UI", 20, "bold"), bg="white")
        title_label.pack(pady=20)

        # Consultations list
        self.consultations_tree = ttk.Treeview(self.content_frame, columns=("ID", "Date", "Nom", "Prénom", "Âge", "Motif"), show="headings")
        self.consultations_tree.heading("ID", text="ID")
        self.consultations_tree.heading("Date", text="Date")
        self.consultations_tree.heading("Nom", text="Nom")
        self.consultations_tree.heading("Prénom", text="Prénom")
        self.consultations_tree.heading("Âge", text="Âge")
        self.consultations_tree.heading("Motif", text="Motif")
        self.consultations_tree.pack(expand=True, fill="both", padx=20, pady=10)

        self.load_consultations()
        
        self.consultations_tree.bind("<Double-1>", self.edit_consultation_from_tree)

    def load_consultations(self):
        for i in self.consultations_tree.get_children():
            self.consultations_tree.delete(i)

        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id, date_consultation, nom_patient, prenom_patient, age, motif_consultation FROM consultations ORDER BY date_consultation DESC")
        for row in cursor.fetchall():
            self.consultations_tree.insert("", "end", values=row)

    def show_new_consultation_view(self):
        self.clear_content_frame()
        
        title_label = tk.Label(self.content_frame, text="Nouvelle Consultation", font=("Segoe UI", 20, "bold"), bg="white")
        title_label.pack(pady=20)

        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(padx=20, pady=10, fill="x")

        # Form fields
        last_row = self.create_consultation_form(form_frame)

        # FIX: Save button goes on a separate row after last field
        save_button = ttk.Button(form_frame, text="Enregistrer", command=self.save_consultation, style="Accent.TButton")
        save_button.grid(row=last_row, column=0, columnspan=2, pady=20, sticky="ew")

    def create_consultation_form(self, parent_frame):
        labels = [
            "Date de consultation",
            "Nom du patient",
            "Prénom du patient",
            "Âge",
            "Motif de consultation",
            "Examen clinique",
            "Examens complémentaires",
            "Traitement"
        ]
        self.form_entries = {}

        for i, label_text in enumerate(labels):
            label = tk.Label(parent_frame, text=label_text, font=("Segoe UI", 12), bg="white")
            label.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            if "consultation" in label_text.lower() or "examen" in label_text.lower() or "traitement" in label_text.lower():
                entry = tk.Text(parent_frame, font=("Segoe UI", 12), height=4, width=50)
            else:
                entry = ttk.Entry(parent_frame, font=("Segoe UI", 12))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.form_entries[label_text] = entry

        parent_frame.grid_columnconfigure(1, weight=1)  # make entry column expand
        return len(labels)  # return the next free row index

    def save_consultation(self):
        values = [
            self.form_entries[label].get("1.0", "end-1c") if isinstance(self.form_entries[label], tk.Text)
            else self.form_entries[label].get()
            for label in self.form_entries
        ]

        cursor = self.db_conn.cursor()
        cursor.execute('''
            INSERT INTO consultations (date_consultation, nom_patient, prenom_patient, age, motif_consultation, examen_clinique, examens_complementaires, traitement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(values))
        self.db_conn.commit()
        messagebox.showinfo("Succès", "Consultation enregistrée avec succès!")
        self.show_consultations_view()

    def edit_consultation_from_tree(self, event):
        item_id = self.consultations_tree.selection()[0]
        consultation_id = self.consultations_tree.item(item_id)['values'][0]
        
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Modifier la consultation")
        self.edit_window.geometry("600x600")

        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM consultations WHERE id = ?", (consultation_id,))
        consultation = cursor.fetchone()

        form_frame = tk.Frame(self.edit_window)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.create_consultation_form(form_frame)
        
        # Populate form
        for i, key in enumerate(self.form_entries.keys()):
            if isinstance(self.form_entries[key], tk.Text):
                self.form_entries[key].insert("1.0", consultation[i+1])
            else:
                self.form_entries[key].insert(0, consultation[i+1])

        update_button = ttk.Button(form_frame, text="Mettre à jour", command=lambda: self.update_consultation(consultation_id), style="Accent.TButton")
        update_button.grid(row=8, column=0, columnspan=2, pady=20, sticky="ew")
        
        delete_button = ttk.Button(form_frame, text="Supprimer", command=lambda: self.delete_consultation(consultation_id), style="Danger.TButton")
        delete_button.grid(row=9, column=0, columnspan=2, pady=10, sticky="ew")

    def update_consultation(self, consultation_id):
        values = [
            self.form_entries[label].get("1.0", "end-1c") if isinstance(self.form_entries[label], tk.Text)
            else self.form_entries[label].get()
            for label in self.form_entries
        ]
        values.append(consultation_id)
        
        cursor = self.db_conn.cursor()
        cursor.execute('''
            UPDATE consultations SET
            date_consultation = ?, nom_patient = ?, prenom_patient = ?, age = ?,
            motif_consultation = ?, examen_clinique = ?, examens_complementaires = ?, traitement = ?
            WHERE id = ?
        ''', tuple(values))
        self.db_conn.commit()
        
        self.edit_window.destroy()
        self.load_consultations()
        messagebox.showinfo("Succès", "Consultation mise à jour avec succès!")

    def delete_consultation(self, consultation_id):
         if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette consultation ?"):
            cursor = self.db_conn.cursor()
            cursor.execute("DELETE FROM consultations WHERE id = ?", (consultation_id,))
            self.db_conn.commit()
            
            self.edit_window.destroy()
            self.load_consultations()
            messagebox.showinfo("Succès", "Consultation supprimée avec succès!")

    def show_stats_view(self):
        self.clear_content_frame()
        
        title_label = tk.Label(self.content_frame, text="Statistiques", font=("Segoe UI", 20, "bold"), bg="white")
        title_label.pack(pady=20)
        
        stats_frame = tk.Frame(self.content_frame, bg="white")
        stats_frame.pack(expand=True)
        
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT COUNT(*), AVG(age) FROM consultations")
        total_consultations, avg_age = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM consultations WHERE date_consultation = ?", (datetime.today().strftime('%Y-%m-%d'),))
        today_consultations = cursor.fetchone()[0]

        total_consultations_label = tk.Label(stats_frame, text=f"Consultations totales: {total_consultations}", font=("Segoe UI", 16), bg="white")
        total_consultations_label.pack(pady=10)
        
        today_consultations_label = tk.Label(stats_frame, text=f"Consultations aujourd'hui: {today_consultations}", font=("Segoe UI", 16), bg="white")
        today_consultations_label.pack(pady=10)

        avg_age_text = f"{avg_age:.2f}" if avg_age else "0"
        avg_age_label = tk.Label(stats_frame, text=f"Âge moyen des patients: {avg_age_text}", font=("Segoe UI", 16), bg="white")
        avg_age_label.pack(pady=10)
        
    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
if __name__ == "__main__":
    root = tk.Tk()
    
    # Styling
    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("TButton", font=("Segoe UI", 12), padding=10)
    style.configure("Accent.TButton", foreground="white", background="#667eea")
    style.configure("Nav.TButton", font=("Segoe UI", 14), padding=15, width=20, background="#f8f9fa")
    style.map("Nav.TButton", background=[("active", "#e9ecef")])
    style.configure("Danger.TButton", foreground="white", background="#dc3545")

    app = CabinetPediatrie(root)
    root.mainloop()
