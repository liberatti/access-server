import sys
import bcrypt
from api.model.user_model import UserDao

def reset_admin(usr, pw):
    dao = UserDao()
    try:
        user = dao.find_by_username(usr)
        if user is None:
            print(f"User with username {usr} not found.")
            return

        hashed_pw = bcrypt.hashpw(pw.encode("utf8"), bcrypt.gensalt())
        dao.update_by_id(user["id"], {"role": "superuser","password": hashed_pw.decode("utf-8")})
        dao.commit()
        print("Password successfully updated.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        dao.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python cli.py reset_admin <username> <new_password>")
        sys.exit(1)

    command = sys.argv[1]
    if command == "reset_admin":
        if len(sys.argv) != 4:
            print("Usage: python cli.py reset_admin <username> <new_password>")
            sys.exit(1)
        
        username = sys.argv[2]
        new_password = sys.argv[3]
        reset_admin(username, new_password)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
