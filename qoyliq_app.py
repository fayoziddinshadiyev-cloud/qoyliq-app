import tkinter as tk
from tkinter import ttk, messagebox
import pg8000.dbapi as pg8000
import os
from datetime import datetime

# ============================================================================
# ПС «ҚЎЙЛИҚ» — Муҳандислик Бошқарув ва Синов Маркази
# ⚠ ҲАҚИҚИЙ PostgreSQL "elektroekspert" БАЗАСИГА УЛАНАДИ (сохта маълумот йўқ!)
# pg8000 ишлатилади — compile/wheel муаммосиз ўрнатилади: pip install pg8000
# ============================================================================

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": int(os.environ.get("PGPORT", "5432")),
    "database": os.environ.get("PGDATABASE", "elektroekspert"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", "12345"),
}

SUBSTATION_ID = 5  # ПС Куйлик

STATUS_UZ = {
    "confirmed": "Тасдиқланган",
    "needs_review": "Текшириш керак",
    "conflict": "Зиддиятли",
    "critical": "Критик",
    "test_pending": "Синов кутилмоқда",
    "extra_in_protocol": "Кулда кушилган",
}
STATUS_EN = {v: k for k, v in STATUS_UZ.items()}
STATUS_COLOR = {
    "confirmed": "#e2f0d9", "needs_review": "#fff3cd", "conflict": "#f8d7da",
    "critical": "#f5b7b1", "test_pending": "#f1f1f1", "extra_in_protocol": "#ffe8b3",
}

ROLE_PERMISSIONS = {
    "Администратор": {"can_edit": True, "can_add": True, "can_manage_users": True},
    "Мухандис":       {"can_edit": True, "can_add": True, "can_manage_users": False},
    "Оператор":       {"can_edit": False, "can_add": False, "can_manage_users": False},
}


def get_conn():
    return pg8000.connect(**DB_CONFIG)


class SubstationMainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ПС КУЙЛИК - Мухандислик Бошкарув ва Синов Маркази")
        self.root.geometry("960x680")
        self.root.config(bg="#f0f2f5")

        self.conn = None
        try:
            self.conn = get_conn()
        except Exception as e:
            messagebox.showerror("Уланиш хатоси", f"PostgreSQL'га уланиб булмади:\n{e}")

        header_frame = tk.Frame(root, bg="#1e293b", pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="ПС КУЙЛИК ПОДСТАНЦИЯСИ - ЖОНЛИ БАЗА",
                 bg="#1e293b", fg="#ffffff", font=("Arial", 15, "bold")).pack()
        tk.Label(header_frame, text="elektroekspert (PostgreSQL) - ускуна турлари буйича катъий параметрлар",
                 bg="#1e293b", fg="#94a3b8", font=("Arial", 10)).pack(pady=2)

        body_frame = tk.Frame(root, bg="#ffffff", bd=1, relief=tk.SOLID, padx=25, pady=20)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(body_frame, text="1. Тизимдаги ролингизни танланг:", font=("Arial", 11, "bold"), bg="#ffffff", fg="#1e293b").pack(anchor="w", pady=(0, 5))

        self.role_var = tk.StringVar(value="Мухандис")
        roles_frame = tk.Frame(body_frame, bg="#ffffff")
        roles_frame.pack(anchor="w", pady=(0, 5))
        for role in ROLE_PERMISSIONS.keys():
            tk.Radiobutton(roles_frame, text=role, variable=self.role_var, value=role,
                           font=("Arial", 10), bg="#ffffff", fg="#334155").pack(side=tk.LEFT, padx=15)

        self.role_note = tk.Label(body_frame, text="", font=("Arial", 9, "italic"), bg="#ffffff", fg="#64748b")
        self.role_note.pack(anchor="w", pady=(0, 15))
        self.role_var.trace_add("write", self.update_role_note)
        self.update_role_note()

        tk.Label(body_frame, text="2. Кучланиш синфини танланг:", font=("Arial", 11, "bold"), bg="#ffffff", fg="#1e293b").pack(anchor="w", pady=(0, 10))

        self.kv_buttons_frame = tk.Frame(body_frame, bg="#ffffff")
        self.kv_buttons_frame.pack(fill=tk.X)
        self.build_kv_buttons()

        btn_refresh = tk.Button(body_frame, text="Кучланиш тугмаларини янгилаш",
                                 bg="#64748b", fg="white", font=("Arial", 9), pady=6, command=self.build_kv_buttons)
        btn_refresh.pack(fill=tk.X, pady=(15, 0))

        tk.Label(root, text="ПС Куйлик | elektroekspert базасига жонли уланган",
                 bg="#e2e8f0", fg="#475569", font=("Arial", 9), anchor="w", padx=15, pady=6).pack(side=tk.BOTTOM, fill=tk.X)

    def update_role_note(self, *args):
        perm = ROLE_PERMISSIONS[self.role_var.get()]
        if perm["can_add"]:
            self.role_note.config(text="Бу ролда кушиш/тахрирлаш хукуки бор.")
        else:
            self.role_note.config(text="Бу ролда факат укиш мумкин (кушиш/тахрирлаш ёпик).")

    def build_kv_buttons(self):
        for w in self.kv_buttons_frame.winfo_children():
            w.destroy()
        if self.conn is None:
            tk.Label(self.kv_buttons_frame, text="База билан уланиш йук", fg="red", bg="#ffffff").pack()
            return
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT vl.voltage_kv, count(*)
                FROM substation_equipment se
                JOIN voltage_levels vl ON vl.id = se.voltage_level_id
                WHERE se.substation_id = %s
                GROUP BY vl.voltage_kv ORDER BY vl.voltage_kv DESC;
            """, (SUBSTATION_ID,))
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            tk.Label(self.kv_buttons_frame, text=f"Суров хатоси: {e}", fg="red", bg="#ffffff", wraplength=600).pack()
            return

        if not rows:
            tk.Label(self.kv_buttons_frame, text="Ускуна топилмади.", bg="#ffffff").pack()
            return

        for kv, cnt in rows:
            kv_num = float(kv)
            btn = tk.Button(self.kv_buttons_frame,
                             text=f"{kv_num:g} кВ ускуналари ({cnt} та)",
                             bg="#2563eb", fg="white", font=("Arial", 11, "bold"), width=44, pady=8,
                             command=lambda v=kv_num: self.open_equipment_list(v))
            btn.pack(pady=4)

    def open_equipment_list(self, voltage_kv):
        role = self.role_var.get()
        perm = ROLE_PERMISSIONS[role]

        list_win = tk.Toplevel(self.root)
        list_win.title(f"ПС Куйлик - {voltage_kv:g} кВ ускуналари")
        list_win.geometry("1100x600")
        list_win.config(bg="#f0f2f5")

        tk.Label(list_win, text=f"ПС Куйлик - {voltage_kv:g} кВ ускуналари (Роль: {role})",
                 font=("Arial", 11, "bold"), bg="#f0f2f5", fg="#1e293b").pack(pady=10)

        table_frame = tk.Frame(list_win)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columns = ("id", "bay", "tag", "cat", "type", "status")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        tree.heading("id", text="ID")
        tree.heading("bay", text="Ячейка / фидер номи")
        tree.heading("tag", text="Asset tag")
        tree.heading("cat", text="Тоифаси")
        tree.heading("type", text="Тури / модели")
        tree.heading("status", text="Холати")

        tree.column("id", width=50, anchor=tk.CENTER)
        tree.column("bay", width=230)
        tree.column("tag", width=150)
        tree.column("cat", width=130)
        tree.column("type", width=220)
        tree.column("status", width=150, anchor=tk.CENTER)

        for code, color in STATUS_COLOR.items():
            tree.tag_configure(code, background=color)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def load_data():
            for r in tree.get_children():
                tree.delete(r)
            cur = self.conn.cursor()
            cur.execute("""
                SELECT se.id, se.bay_name, se.asset_tag,
                       COALESCE(et.category, '-') AS category,
                       COALESCE(et.type_name, '-') AS type_name,
                       se.verification_status
                FROM substation_equipment se
                JOIN voltage_levels vl ON vl.id = se.voltage_level_id
                LEFT JOIN equipment_models em ON em.id = se.equipment_model_id
                LEFT JOIN equipment_types et ON et.id = em.equipment_type_id
                WHERE se.substation_id = %s AND vl.voltage_kv = %s
                ORDER BY se.bay_name;
            """, (SUBSTATION_ID, voltage_kv))
            for r in cur.fetchall():
                eq_id, bay, tag, cat, typ, status = r
                tree.insert("", tk.END, values=(eq_id, bay, tag or "-", cat, typ, STATUS_UZ.get(status, status)), tags=(status,))
            cur.close()

        load_data()

        def on_select(event):
            selected = tree.selection()
            if not selected:
                return
            item_vals = tree.item(selected)['values']
            self.open_equipment_detail(list_win, item_vals[0], role, perm, load_data)

        tree.bind("<Double-1>", on_select)

        btn_frame = tk.Frame(list_win, bg="#f0f2f5")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)

        if perm["can_add"]:
            tk.Button(btn_frame, text="+ Кулда янги ускуна кушиш", bg="#16a34a", fg="white",
                      font=("Arial", 10, "bold"), pady=6,
                      command=lambda: self.open_add_manual_window(list_win, voltage_kv, load_data)
                      ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        else:
            tk.Label(btn_frame, text="Оператор ролида кушиш хукуки йук (факат укиш)",
                      bg="#f0f2f5", fg="#94a3b8", font=("Arial", 9, "italic")).pack(side=tk.LEFT, expand=True)

        tk.Button(btn_frame, text="Оркага", bg="#64748b", fg="white", font=("Arial", 10, "bold"),
                  pady=6, command=list_win.destroy).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    def open_add_manual_window(self, parent, voltage_kv, refresh_callback):
        add_win = tk.Toplevel(parent)
        add_win.title("Янги ускуна кулда кушиш")
        add_win.geometry("480x480")
        add_win.config(bg="#ffffff")

        tk.Label(add_win, text=f"Янги ускуна кушиш ({voltage_kv:g} кВ)", font=("Arial", 11, "bold"), bg="#ffffff").pack(pady=12)

        def field(label):
            tk.Label(add_win, text=label, font=("Arial", 9, "bold"), bg="#ffffff").pack(anchor="w", padx=30)
            e = tk.Entry(add_win, width=48, font=("Arial", 10))
            e.pack(padx=30, pady=(2, 8))
            return e

        bay_entry = field("Ячейка / фидер номи:")
        tag_entry = field("Asset tag (нoyob код, мас: FDR-YANGI-1):")
        cat_entry = field("Тоифа (мас: breaker, disconnector, CT):")
        type_entry = field("Тури / модели (мас: ВМГ-133):")
        serial_entry = field("Зав.№ (ихтиёрий):")

        def save_item():
            bay = bay_entry.get().strip()
            tag = tag_entry.get().strip()
            cat = cat_entry.get().strip()
            typ = type_entry.get().strip()
            serial = serial_entry.get().strip() or None

            if not bay or not tag or not cat or not typ:
                messagebox.showerror("Хатолик", "Ячейка, Asset tag, Тоифа ва Тури тулдирилиши шарт!")
                return

            try:
                cur = self.conn.cursor()
                cur.execute("SELECT id FROM equipment_types WHERE type_name = %s", (typ,))
                row = cur.fetchone()
                if row:
                    type_id = row[0]
                else:
                    cur.execute("INSERT INTO equipment_types (type_name, category) VALUES (%s, %s) RETURNING id", (typ, cat))
                    type_id = cur.fetchone()[0]

                cur.execute("SELECT id FROM equipment_models WHERE model_name = %s", (typ,))
                row = cur.fetchone()
                if row:
                    model_id = row[0]
                else:
                    cur.execute("INSERT INTO equipment_models (model_name, equipment_type_id) VALUES (%s, %s) RETURNING id", (typ, type_id))
                    model_id = cur.fetchone()[0]

                cur.execute("SELECT id FROM voltage_levels WHERE voltage_kv = %s", (voltage_kv,))
                vl_row = cur.fetchone()
                if not vl_row:
                    messagebox.showerror("Хатолик", f"{voltage_kv} кВ учун voltage_levels топилмади!")
                    return
                vl_id = vl_row[0]

                cur.execute("""
                    INSERT INTO substation_equipment
                        (bay_name, equipment_model_id, voltage_level_id, substation_id,
                         asset_tag, serial_number, verification_status, status_comment)
                    VALUES (%s, %s, %s, %s, %s, %s, 'extra_in_protocol', %s)
                """, (bay, model_id, vl_id, SUBSTATION_ID, tag, serial,
                      "Кулда кушилди (дастур оркали)"))
                self.conn.commit()
                cur.close()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Саклаш хатоси", str(e))
                return

            messagebox.showinfo("Муваффакиятли", "Янги ускуна базага кушилди!")
            refresh_callback()
            add_win.destroy()

        tk.Button(add_win, text="Саклаш", bg="#16a34a", fg="white", font=("Arial", 10, "bold"),
                  width=20, command=save_item).pack(pady=15)

    def open_equipment_detail(self, parent, eq_id, role, perm, refresh_callback):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT se.bay_name, se.asset_tag, se.serial_number, vl.voltage_kv,
                   COALESCE(et.category,'-'), COALESCE(et.type_name,'-'),
                   se.verification_status, se.status_comment
            FROM substation_equipment se
            JOIN voltage_levels vl ON vl.id = se.voltage_level_id
            LEFT JOIN equipment_models em ON em.id = se.equipment_model_id
            LEFT JOIN equipment_types et ON et.id = em.equipment_type_id
            WHERE se.id = %s
        """, (eq_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return
        bay_name, asset_tag, serial, kv, category, type_name, status_code, status_comment = row
        kv = float(kv)
        status_ru = STATUS_UZ.get(status_code, status_code)

        det_win = tk.Toplevel(parent)
        det_win.title(f"Ускуна паспорти: {asset_tag}")
        det_win.geometry("820x680")
        det_win.config(bg="#f8fafc")

        header_card = tk.Frame(det_win, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=10)
        header_card.pack(fill=tk.X, padx=15, pady=8)
        tk.Label(header_card, text=f"{bay_name}", font=("Arial", 12, "bold"), bg="#ffffff", fg="#1e293b").pack(anchor="w")
        tk.Label(header_card,
                 text=f"Asset Tag: {asset_tag} | Зав.No: {serial or '-'} | Кучланиш: {kv:g} кВ | Тоифа: {category} | Тури: {type_name}",
                 font=("Arial", 9, "bold"), bg="#ffffff", fg="#2563eb", wraplength=760, justify=tk.LEFT).pack(anchor="w", pady=2)
        if status_comment:
            tk.Label(header_card, text=f"Изох: {status_comment}", font=("Arial", 9), bg="#ffffff",
                     fg="#856404", wraplength=760, justify=tk.LEFT).pack(anchor="w", pady=2)

        form_frame = tk.Frame(det_win, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=10)
        form_frame.pack(fill=tk.X, padx=15, pady=4)
        tk.Label(form_frame, text="Холатни узгартириш:", font=("Arial", 9, "bold"), bg="#ffffff").pack(anchor="w")
        status_combo = ttk.Combobox(form_frame, values=list(STATUS_UZ.values()), state="readonly", font=("Arial", 10), width=40)
        status_combo.set(status_ru)
        status_combo.pack(anchor="w", pady=3)
        if not perm["can_edit"]:
            status_combo.config(state="disabled")

        def save_status():
            if not perm["can_edit"]:
                messagebox.showerror("Рухсат йук", "Оператор ролида узгартириш мумкин эмас!")
                return
            new_code = STATUS_EN.get(status_combo.get(), "confirmed")
            try:
                c = self.conn.cursor()
                c.execute("UPDATE substation_equipment SET verification_status=%s WHERE id=%s", (new_code, eq_id))
                self.conn.commit()
                c.close()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Хато", str(e))
                return
            messagebox.showinfo("Муваффакиятли", "Холат янгиланди!")
            refresh_callback()
            det_win.destroy()

        save_btn = tk.Button(form_frame, text="Холатни саклаш", bg="#16a34a" if perm["can_edit"] else "#94a3b8",
                              fg="white", font=("Arial", 9, "bold"), padx=10, pady=5,
                              command=save_status, state=(tk.NORMAL if perm["can_edit"] else tk.DISABLED))
        save_btn.pack(anchor="w", pady=5)

        test_frame = tk.Frame(det_win, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=10)
        test_frame.pack(fill=tk.X, padx=15, pady=4)
        tk.Label(test_frame, text="Янги синов натижаси кушиш:", font=("Arial", 9, "bold"), bg="#ffffff").pack(anchor="w")

        row1 = tk.Frame(test_frame, bg="#ffffff"); row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text="Rиз/R60 (МОм):", bg="#ffffff", width=16, anchor="w").pack(side=tk.LEFT)
        r60_entry = tk.Entry(row1, width=15); r60_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(row1, text="tgd (%):", bg="#ffffff", width=10, anchor="w").pack(side=tk.LEFT)
        tgd_entry = tk.Entry(row1, width=15); tgd_entry.pack(side=tk.LEFT, padx=5)

        row2 = tk.Frame(test_frame, bg="#ffffff"); row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text="Хулоса:", bg="#ffffff", width=16, anchor="w").pack(side=tk.LEFT)
        concl_entry = tk.Entry(row2, width=40); concl_entry.pack(side=tk.LEFT, padx=5)

        row3 = tk.Frame(test_frame, bg="#ffffff"); row3.pack(fill=tk.X, pady=2)
        tk.Label(row3, text="Изох:", bg="#ffffff", width=16, anchor="w").pack(side=tk.LEFT)
        note_entry = tk.Entry(row3, width=52); note_entry.pack(side=tk.LEFT, padx=5)

        def add_test():
            if not perm["can_add"]:
                messagebox.showerror("Рухсат йук", "Оператор ролида синов кушиш мумкин эмас!")
                return

            def to_float(s):
                s = s.strip().replace(",", ".")
                return float(s) if s else None

            try:
                r60 = to_float(r60_entry.get())
                tgd = to_float(tgd_entry.get())
            except ValueError:
                messagebox.showerror("Хатолик", "Rиз/tgd ракам булиши керак!")
                return

            try:
                c = self.conn.cursor()
                c.execute("""
                    INSERT INTO maintenance_logs
                        (equipment_id, maintenance_date, maintenance_type, r60_mohm, tg_delta_pct,
                         conclusion, description, verification_status, technician_name)
                    VALUES (%s, %s, 'изоляция синови', %s, %s, %s, %s, 'confirmed', %s)
                """, (eq_id, datetime.now(), r60, tgd, concl_entry.get().strip() or "Норма",
                      note_entry.get().strip() or None, role))
                self.conn.commit()
                c.close()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Саклаш хатоси", str(e))
                return

            messagebox.showinfo("Муваффакиятли", "Синов натижаси кушилди!")
            load_history()
            r60_entry.delete(0, tk.END); tgd_entry.delete(0, tk.END)
            concl_entry.delete(0, tk.END); note_entry.delete(0, tk.END)

        add_btn = tk.Button(test_frame, text="Синовни саклаш", bg="#16a34a" if perm["can_add"] else "#94a3b8",
                             fg="white", font=("Arial", 9, "bold"), padx=10, pady=5,
                             command=add_test, state=(tk.NORMAL if perm["can_add"] else tk.DISABLED))
        add_btn.pack(anchor="w", pady=5)

        history_frame = tk.Frame(det_win, bg="#ffffff", bd=1, relief=tk.SOLID, padx=10, pady=8)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(4, 12))
        tk.Label(history_frame, text="Синов тарихи:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#1e293b").pack(anchor="w", pady=3)

        hist_tree = ttk.Treeview(history_frame, columns=("date", "r60", "tgd", "concl", "note"), show="headings", height=8)
        hist_tree.heading("date", text="Сана")
        hist_tree.heading("r60", text="R60 (МОм)")
        hist_tree.heading("tgd", text="tgd (%)")
        hist_tree.heading("concl", text="Хулоса")
        hist_tree.heading("note", text="Изох")
        hist_tree.column("date", width=110, anchor=tk.CENTER)
        hist_tree.column("r60", width=90, anchor=tk.CENTER)
        hist_tree.column("tgd", width=80, anchor=tk.CENTER)
        hist_tree.column("concl", width=150)
        hist_tree.column("note", width=280)
        hist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def load_history():
            for r in hist_tree.get_children():
                hist_tree.delete(r)
            c = self.conn.cursor()
            c.execute("""
                SELECT maintenance_date, r60_mohm, tg_delta_pct, conclusion, description
                FROM maintenance_logs WHERE equipment_id = %s ORDER BY maintenance_date DESC
            """, (eq_id,))
            for d, r60v, tgdv, concl, note in c.fetchall():
                date_str = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
                hist_tree.insert("", tk.END, values=(date_str, r60v if r60v is not None else "-",
                                                      tgdv if tgdv is not None else "-", concl or "-", note or "-"))
            c.close()

        load_history()


if __name__ == "__main__":
    root = tk.Tk()
    app = SubstationMainApp(root)
    root.mainloop()
