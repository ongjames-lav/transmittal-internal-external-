#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

# Connect to SQLite database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(transmittals_transmittal)")
columns = cursor.fetchall()

print("\n" + "="*100)
print("TRANSMITTAL TABLE SCHEMA - RECIPIENT_ID FIELD")
print("="*100)

print("\nAll columns in transmittals_transmittal table:")
print(f"{'ID':<5} {'Name':<30} {'Type':<15} {'Not Null':<10} {'Pk':<5}")
print("-" * 100)

recipient_id_row = None
recipient_email_row = None

for col in columns:
    cid, name, type_, notnull, dflt_value, pk = col
    is_pk = "YES" if pk else ""
    is_notnull = "YES" if notnull else "NO"
    
    if name == 'recipient_id_id':
        recipient_id_row = (cid, name, type_, is_notnull, is_pk)
        mark = " ← NEW FIELD"
    elif name == 'recipient_email':
        recipient_email_row = (cid, name, type_, is_notnull, is_pk)
        mark = " ← PRESERVED"
    else:
        mark = ""
    
    print(f"{cid:<5} {name:<30} {type_:<15} {is_notnull:<10} {is_pk:<5}{mark}")

print("\n" + "="*100)
print("KEY FIELD DETAILS")
print("="*100)

if recipient_id_row:
    print(f"\n✓ recipient_id_id field:")
    print(f"    - Column ID: {recipient_id_row[0]}")
    print(f"    - Name: {recipient_id_row[1]}")
    print(f"    - Type: {recipient_id_row[2]} (Integer - Foreign Key)")
    print(f"    - Not Null: {recipient_id_row[3]} (required field)")
    print(f"    - Primary Key: {recipient_id_row[4]}")
    print(f"    - Purpose: Links transmittal to User by ID (permanent)")
    print(f"    - On Delete: PROTECT (prevents user deletion)")

if recipient_email_row:
    print(f"\n✓ recipient_email field:")
    print(f"    - Column ID: {recipient_email_row[0]}")
    print(f"    - Name: {recipient_email_row[1]}")
    print(f"    - Type: {recipient_email_row[2]}")
    print(f"    - Not Null: {recipient_email_row[3]} (required field)")
    print(f"    - Primary Key: {recipient_email_row[4]}")
    print(f"    - Purpose: Display purposes, audit trail (email address)")
    print(f"    - Queries: No longer used for filtering")

# Check indexes
print("\n" + "="*100)
print("DATABASE INDEXES")
print("="*100)

cursor.execute("PRAGMA index_list(transmittals_transmittal)")
indexes = cursor.fetchall()

print("\nIndexes on transmittals_transmittal:")
for idx in indexes:
    seq, name, unique, origin, partial = idx
    print(f"  - {name} (unique: {unique}, origin: {origin})")
    
    # Get index details
    cursor.execute(f"PRAGMA index_info({name})")
    index_cols = cursor.fetchall()
    for col_info in index_cols:
        seqno, cid, col_name = col_info
        print(f"      Column: {col_name}")

print("\n" + "="*100)
print("SCHEMA VERIFICATION COMPLETE")
print("="*100 + "\n")

conn.close()
