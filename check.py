import sqlite3
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('instance/database.db')  # Update with your actual database path
cursor = conn.cursor()

# Fetch all jobs to check the data
cursor.execute("SELECT id, date_posted FROM Job")
jobs = cursor.fetchall()

# Print jobs to inspect the current state of date_posted
print("Before Update:")
for job in jobs:
    print(job)

# Update the date_posted field
for job in jobs:
    job_id = job[0]
    cursor.execute("UPDATE Job SET date_posted = ? WHERE id = ?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), job_id))

# Commit the changes
conn.commit()

# Fetch updated jobs to verify the change
cursor.execute("SELECT id, date_posted FROM Job")
updated_jobs = cursor.fetchall()

# Print jobs to inspect the updated state of date_posted
print("After Update:")
for job in updated_jobs:
    print(job)

# Close the connection
conn.close()
