import pymysql

pwds = ['root123', '', 'root', '1234', '123456', 'admin', 'password', 'kamepalli', 'akhilesh', 'kamepalli@123', 'akhilesh@123', 'root@123', 'Admin@123']

found = False
for pwd in pwds:
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password=pwd)
        print(f"FOUND WORKING PASSWORD: '{pwd}'")
        found = True
        conn.close()
        break
    except Exception as e:
        pass

if not found:
    print("Could not connect with common passwords.")
