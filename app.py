"""
Customer Service Ticket Management System
Portfolio Project - Python + SQLite

Run:
    python app.py
or:
    py app.py
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("customer_service.db")

CATEGORIES = {
    "1": "Account",
    "2": "Payment",
    "3": "Order",
    "4": "Technical Issue",
    "5": "Complaint",
    "6": "Information",
    "7": "Other",
}

PRIORITIES = {
    "1": "Low",
    "2": "Medium",
    "3": "High",
}

STATUSES = {
    "1": "Open",
    "2": "In Progress",
    "3": "Resolved",
    "4": "Closed",
}


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT DEFAULT '',
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Open',
                solution TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def pause():
    input("\nTekan Enter untuk kembali ke menu...")


def ask(prompt, required=False, default=""):
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"{prompt}{suffix}: ").strip()
        value = value or default

        if required and not value:
            print("Data ini wajib diisi.")
            continue

        return value


def generate_ticket_number(con=None):
    """Buat nomor tiket unik.

    Jika koneksi database diberikan, gunakan koneksi yang sama agar perubahan
    yang belum di-commit (misalnya saat mengisi data demo) tetap terbaca.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if con is not None:
        count = con.execute(
            "SELECT COUNT(*) AS total FROM tickets"
        ).fetchone()["total"]
    else:
        with connect() as db:
            count = db.execute(
                "SELECT COUNT(*) AS total FROM tickets"
            ).fetchone()["total"]

    return f"CS-{timestamp}-{count + 1:03d}"


def create_ticket():
    print("\n=== INPUT TIKET CUSTOMER ===")

    customer_name = ask("Nama customer", True)
    phone = ask("Nomor telepon", True)
    email = ask("Email")

    print("\nKategori:")
    for key, value in CATEGORIES.items():
        print(f"{key}. {value}")
    category_choice = ask("Pilih kategori", True)

    if category_choice not in CATEGORIES:
        print("Kategori tidak valid.")
        return

    print("\nPrioritas:")
    for key, value in PRIORITIES.items():
        print(f"{key}. {value}")
    priority_choice = ask("Pilih prioritas", True)

    if priority_choice not in PRIORITIES:
        print("Prioritas tidak valid.")
        return

    subject = ask("Subjek masalah", True)
    description = ask("Deskripsi masalah")

    now = datetime.now().isoformat(timespec="seconds")
    ticket_number = generate_ticket_number()

    with connect() as con:
        con.execute("""
            INSERT INTO tickets (
                ticket_number,
                customer_name,
                phone,
                email,
                category,
                priority,
                subject,
                description,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_number,
            customer_name,
            phone,
            email,
            CATEGORIES[category_choice],
            PRIORITIES[priority_choice],
            subject,
            description,
            "Open",
            now,
            now
        ))

    print(f"\nTiket berhasil dibuat: {ticket_number}")


def list_tickets():
    with connect() as con:
        rows = con.execute("""
            SELECT
                id,
                ticket_number,
                customer_name,
                category,
                priority,
                subject,
                status,
                created_at
            FROM tickets
            ORDER BY id DESC
        """).fetchall()

    print("\n=== DAFTAR TIKET ===")

    if not rows:
        print("Belum ada tiket.")
        return

    print("-" * 120)
    print(
        f"{'ID':<4} "
        f"{'Ticket':<22} "
        f"{'Customer':<20} "
        f"{'Kategori':<18} "
        f"{'Prioritas':<10} "
        f"{'Status':<14} "
        f"{'Subjek':<25}"
    )
    print("-" * 120)

    for row in rows:
        print(
            f"{row['id']:<4} "
            f"{row['ticket_number']:<22} "
            f"{row['customer_name'][:19]:<20} "
            f"{row['category'][:17]:<18} "
            f"{row['priority']:<10} "
            f"{row['status']:<14} "
            f"{row['subject'][:24]:<25}"
        )

    print("-" * 120)


def get_ticket(ticket_id):
    with connect() as con:
        return con.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()


def view_ticket():
    list_tickets()

    try:
        ticket_id = int(ask("\nMasukkan ID tiket", True))
    except ValueError:
        print("ID harus berupa angka.")
        return

    ticket = get_ticket(ticket_id)

    if not ticket:
        print("Tiket tidak ditemukan.")
        return

    print("\n=== DETAIL TIKET ===")
    print(f"Ticket Number : {ticket['ticket_number']}")
    print(f"Customer      : {ticket['customer_name']}")
    print(f"Phone         : {ticket['phone']}")
    print(f"Email         : {ticket['email'] or '-'}")
    print(f"Category      : {ticket['category']}")
    print(f"Priority      : {ticket['priority']}")
    print(f"Subject       : {ticket['subject']}")
    print(f"Description   : {ticket['description'] or '-'}")
    print(f"Status        : {ticket['status']}")
    print(f"Solution      : {ticket['solution'] or '-'}")
    print(f"Created       : {ticket['created_at']}")
    print(f"Updated       : {ticket['updated_at']}")


def update_ticket():
    list_tickets()

    try:
        ticket_id = int(ask("\nID tiket yang ingin diperbarui", True))
    except ValueError:
        print("ID harus berupa angka.")
        return

    ticket = get_ticket(ticket_id)

    if not ticket:
        print("Tiket tidak ditemukan.")
        return

    print("\nStatus:")
    for key, value in STATUSES.items():
        print(f"{key}. {value}")

    status_choice = ask(
        "Pilih status",
        True,
        default=""
    )

    if status_choice not in STATUSES:
        print("Status tidak valid.")
        return

    solution = ask(
        "Catatan solusi/tindakan CS",
        default=ticket["solution"]
    )

    now = datetime.now().isoformat(timespec="seconds")

    with connect() as con:
        con.execute("""
            UPDATE tickets
            SET status = ?,
                solution = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            STATUSES[status_choice],
            solution,
            now,
            ticket_id
        ))

    print("Tiket berhasil diperbarui.")


def search_ticket():
    keyword = ask("\nMasukkan nama customer, nomor tiket, atau subjek", True)

    pattern = f"%{keyword}%"

    with connect() as con:
        rows = con.execute("""
            SELECT *
            FROM tickets
            WHERE customer_name LIKE ?
               OR ticket_number LIKE ?
               OR subject LIKE ?
               OR phone LIKE ?
            ORDER BY id DESC
        """, (
            pattern,
            pattern,
            pattern,
            pattern
        )).fetchall()

    print("\n=== HASIL PENCARIAN ===")

    if not rows:
        print("Tidak ditemukan tiket yang sesuai.")
        return

    for row in rows:
        print(
            f"\n{row['ticket_number']} | "
            f"{row['customer_name']} | "
            f"{row['status']}"
        )
        print(f"Kategori : {row['category']}")
        print(f"Prioritas: {row['priority']}")
        print(f"Subjek   : {row['subject']}")


def dashboard():
    with connect() as con:
        total = con.execute(
            "SELECT COUNT(*) AS total FROM tickets"
        ).fetchone()["total"]

        open_count = con.execute(
            "SELECT COUNT(*) AS total FROM tickets WHERE status='Open'"
        ).fetchone()["total"]

        progress = con.execute(
            "SELECT COUNT(*) AS total FROM tickets WHERE status='In Progress'"
        ).fetchone()["total"]

        resolved = con.execute(
            "SELECT COUNT(*) AS total FROM tickets WHERE status='Resolved'"
        ).fetchone()["total"]

        closed = con.execute(
            "SELECT COUNT(*) AS total FROM tickets WHERE status='Closed'"
        ).fetchone()["total"]

        high_priority = con.execute(
            "SELECT COUNT(*) AS total FROM tickets WHERE priority='High'"
        ).fetchone()["total"]

        categories = con.execute("""
            SELECT category, COUNT(*) AS total
            FROM tickets
            GROUP BY category
            ORDER BY total DESC
        """).fetchall()

    print("\n" + "=" * 50)
    print("       CUSTOMER SERVICE DASHBOARD")
    print("=" * 50)
    print(f"Total tiket          : {total}")
    print(f"Open                 : {open_count}")
    print(f"In Progress          : {progress}")
    print(f"Resolved             : {resolved}")
    print(f"Closed               : {closed}")
    print(f"Prioritas High       : {high_priority}")

    print("\nTiket berdasarkan kategori:")
    if categories:
        for row in categories:
            print(f"  {row['category']:<20} {row['total']}")
    else:
        print("  Belum ada data.")


def export_csv():
    destination = Path(__file__).with_name("customer_service_report.csv")

    with connect() as con:
        rows = con.execute("""
            SELECT
                ticket_number,
                customer_name,
                phone,
                email,
                category,
                priority,
                subject,
                description,
                status,
                solution,
                created_at,
                updated_at
            FROM tickets
            ORDER BY id
        """).fetchall()

    with destination.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Ticket Number",
            "Customer Name",
            "Phone",
            "Email",
            "Category",
            "Priority",
            "Subject",
            "Description",
            "Status",
            "Solution",
            "Created At",
            "Updated At"
        ])

        for row in rows:
            writer.writerow(tuple(row))

    print(f"\nLaporan berhasil dibuat: {destination.name}")


def seed_demo():
    with connect() as con:
        total = con.execute(
            "SELECT COUNT(*) AS total FROM tickets"
        ).fetchone()["total"]

        if total > 0:
            print("Database sudah memiliki data. Demo tidak ditambahkan.")
            return

        demo = [
            (
                "Andi Pratama",
                "081234567890",
                "andi@email.com",
                "Payment",
                "High",
                "Pembayaran belum masuk",
                "Customer sudah melakukan pembayaran tetapi saldo belum bertambah.",
                "Resolved",
                "Verifikasi transaksi dan melakukan pengecekan pembayaran."
            ),
            (
                "Siti Rahma",
                "081234567891",
                "siti@email.com",
                "Account",
                "Medium",
                "Tidak bisa login",
                "Customer lupa password dan tidak menerima email reset.",
                "In Progress",
                "Meminta customer melakukan verifikasi data."
            ),
            (
                "Budi Santoso",
                "081234567892",
                "budi@email.com",
                "Order",
                "Low",
                "Status pesanan belum berubah",
                "Customer menanyakan status pesanan.",
                "Closed",
                "Memberikan informasi status pengiriman."
            ),
            (
                "Rina Amelia",
                "081234567893",
                "rina@email.com",
                "Complaint",
                "High",
                "Pesanan terlambat",
                "Customer menyampaikan keluhan mengenai keterlambatan.",
                "Open",
                "",
            )
        ]

        now = datetime.now().isoformat(timespec="seconds")

        for customer, phone, email, category, priority, subject, description, status, solution in demo:
            ticket_number = generate_ticket_number(con)

            con.execute("""
                INSERT INTO tickets (
                    ticket_number,
                    customer_name,
                    phone,
                    email,
                    category,
                    priority,
                    subject,
                    description,
                    status,
                    solution,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_number,
                customer,
                phone,
                email,
                category,
                priority,
                subject,
                description,
                status,
                solution,
                now,
                now
            ))

    print("4 data demo berhasil ditambahkan.")


def main():
    init_db()

    while True:
        print("""
========================================
 CUSTOMER SERVICE TICKET MANAGEMENT
========================================

1. Dashboard
2. Lihat semua tiket
3. Input tiket customer
4. Lihat detail tiket
5. Update tiket
6. Cari tiket
7. Export laporan CSV
8. Isi data demo
0. Keluar
""")

        choice = input("Pilih menu: ").strip()

        actions = {
            "1": dashboard,
            "2": list_tickets,
            "3": create_ticket,
            "4": view_ticket,
            "5": update_ticket,
            "6": search_ticket,
            "7": export_csv,
            "8": seed_demo,
        }

        if choice == "0":
            print("Program selesai.")
            break

        action = actions.get(choice)

        if action:
            action()
            pause()
        else:
            print("Pilihan menu tidak tersedia.")


if __name__ == "__main__":
    main()
