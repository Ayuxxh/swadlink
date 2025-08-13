# import subprocess
# import datetime
# import os
# from decouple import config
# # ==== Render DB Connection Details ====
# DB_HOST = config('DB_HOST')
# DB_NAME = config("DB_NAME")
# DB_USER = config('DB_USER')
# DB_PASSWORD = config('DB_PASSWORD')
# DB_PORT = "5432"

# # ==== Output File ====
# date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# backup_file = f"qrahi_backup_{date_str}.sql"

# # ==== Ensure pg_dump is in PATH ====
# # If it's not, put full path here, e.g.: r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"
# PG_DUMP_PATH =  r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"


# # ==== Run pg_dump ====
# os.environ["PGPASSWORD"] = DB_PASSWORD  # avoid password prompt

# cmd = [
#     PG_DUMP_PATH,
#     "-h", DB_HOST,
#     "-p", DB_PORT,
#     "-U", DB_USER,
#     "--no-owner",
#     "--no-privileges",
#     DB_NAME
# ]

# print(f"📦 Starting backup for database '{DB_NAME}' from {DB_HOST}...")
# with open(backup_file, "w", encoding="utf-8") as f:
#     result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)

# if result.returncode == 0:
#     print(f"✅ Backup completed successfully: {backup_file}")
# else:
#     print(f"❌ Backup failed:\n{result.stderr}")


import subprocess
import os
import sys

# ==== Render DB Connection Details ====
DB_HOST = "dpg-d2edml49c44c738s8nvg-a.singapore-postgres.render.com"
DB_NAME = "testdb_le3j"
DB_USER = "testdb_le3j_user"
DB_PASSWORD = "hnK44pCyLvkgCt5uC5OMcsc8pRJ4H9ob"
DB_PORT = "5432"

# ==== Path to your .sql backup ====
# Can be passed as a command-line argument
if len(sys.argv) < 2:
    print("❌ Please provide the path to your SQL backup file.")
    print("Usage: python restore_qrahi.py qrahi_backup.sql")
    sys.exit(1)

backup_file = sys.argv[1]

# ==== Path to psql ====
# If not in PATH, give the full path (example for Windows):
# PSQL_PATH = r"C:\Program Files\PostgreSQL\16\bin\psql.exe"
PSQL_PATH = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"

# ==== Run psql restore ====
os.environ["PGPASSWORD"] = DB_PASSWORD  # avoid password prompt

cmd = [
    PSQL_PATH,
    "-h", DB_HOST,
    "-p", DB_PORT,
    "-U", DB_USER,
    "-d", DB_NAME,
    "-f", backup_file,
   " --set ON_ERROR_STOP=on"

]

print(f"📥 Restoring backup '{backup_file}' into database '{DB_NAME}'...")
result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

if result.returncode == 0:
    print(f"✅ Restore completed successfully!")
else:
    print(f"❌ Restore failed:\n{result.stderr}")
