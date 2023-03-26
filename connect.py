import sqlite3

conn = sqlite3.connect('printer_log.db')
c = conn.cursor()
c.execute('''CREATE TABLE print_log
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              command TEXT NOT NULL,
              response TEXT NOT NULL);''')
conn.commit()
conn.close()