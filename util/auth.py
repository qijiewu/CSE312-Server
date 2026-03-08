from util.response import Response
import bcrypt
import uuid
from util.database import user_collection, chat_collection
import hashlib

def extract_credentials(request):
    body = request.body.decode()
    part = body.split("&")
    username = ""
    password = ""
    for i in part:
        info = i.split("=", 1)
        key, value = info[0], info[1]
        if key == "username":
            username = value
        elif key == "password":
            password = value
    percent_decoded = []
    p = 0
    while p < len(password):
        if password[p] == "%":
            hex_value = password[p+1:p+3]
            byte = bytes.fromhex(hex_value)
            ascii_value = byte.decode()
            percent_decoded.append(ascii_value)
            p += 3
        else:
            percent_decoded.append(password[p])
            p += 1

    password = "".join(percent_decoded)
    return [username, password]

def validate_password(password):
    lowercase = 0
    uppercase = 0
    number = 0
    special = 0
    special_char = ['!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '=']
    for word in password:
        if word.islower():
            lowercase += 1
        elif word.isupper():
            uppercase += 1
        elif word.isdigit():
            number += 1
        elif word in special_char:
            special += 1
        else: #invalid case
            return False
    if len(password) >=8 and lowercase >= 1 and uppercase >= 1 and number >= 1 and special >= 1:
        return True

    return False

def registration(request, handler):
    res = Response()
    username, password = extract_credentials(request)
    user = user_collection.find_one({"username": username})
    if user is not None:
        res.set_status(400, "Invalid")
        res.text("Username Already Exists")
        handler.request.sendall(res.to_data())
        return
    if validate_password(password):
        hash_pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user_collection.insert_one(
            {
                "id": str(uuid.uuid4()),
                "username": username,
                "password": hash_pwd
            }
        )
        res.set_status(200, "OK")
        res.text("Account Created")
        handler.request.sendall(res.to_data())
        return
    else:
        res.set_status(400, "Invalid")
        res.text("Insufficient Password Strength")
        handler.request.sendall(res.to_data())
        return

def login(request, handler):
    res = Response()
    username, password = extract_credentials(request)
    user = user_collection.find_one({"username": username})
    cookie_dict = {}
    if user is None:
        res.set_status(400, "User Does Not Exist")
        res.text("User Does Not Exist")
        handler.request.sendall(res.to_data())
        return
    else:
        if bcrypt.checkpw(password.encode(), user["password"]):
            auth_token = str(uuid.uuid4())
            cookie_dict["auth_token"] = auth_token + "; Max-Age=3600; HttpOnly"
            res.cookies(cookie_dict)
            hash_token = hashlib.sha256(auth_token.encode()).hexdigest()
            user_collection.update_one(
                {"username": username},
                {"$set": {"auth_token": hash_token}}
            )
            res.set_status(200, "OK")
            res.text("Verified")
        else:
            res.set_status(400, "Incorrect Password")
            res.text("Incorrect Password")

    handler.request.sendall(res.to_data())

def logout(request, handler):
    res = Response()
    auth_token = request.cookies.get("auth_token")
    if auth_token is not None:
        hash_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user_collection.update_one(
            {"auth_token": hash_token},
            {"$set": {"auth_token": None}}
        )
    res.cookies({"auth_token": "; Max-Age=0; HttpOnly"})
    res.set_status(302, "Found")
    res.headers({"Location": "/"})

    handler.request.sendall(res.to_data())

def get_profile(request, handler):
    res = Response()
    auth_token = request.cookies.get("auth_token")
    if auth_token is not None:
        hash_token = hashlib.sha256(auth_token.encode()).hexdigest()
        profile = user_collection.find_one({"auth_token": hash_token})
        profile.pop("password")
        profile.pop("auth_token")
        profile.pop("_id")
        res.json(profile)
        res.set_status(200, "OK")
    else:
        res.json({})
        res.set_status(401, "Unauthorized")

    handler.request.sendall(res.to_data())

def search_user(request, handler):
    res = Response()
    split = request.path.split("?", 1)
    search_list = []
    return_dict = {"users": search_list}
    if len(split) == 2:
        query = split[1].split("=", 1)
        if len(query) == 2:
            if query[0] == "user" and query[1] != "":
                users = user_collection.find({})
                for user in users:
                    if user["username"].startswith(query[1]):
                        search_dict = {"id": user["id"], "username": user["username"]}
                        search_list.append(search_dict)
    res.json(return_dict)
    handler.request.sendall(res.to_data())

def update_profile(request, handler):
    res = Response()
    username, password = extract_credentials(request)
    auth_token = request.cookies.get("auth_token")
    hash_token = hashlib.sha256(auth_token.encode()).hexdigest()
    user = user_collection.find_one({"auth_token": hash_token})
    if auth_token is not None:
        if hash_token == user["auth_token"]:
            if password == "":
                user_collection.update_one(
                    {"auth_token": hash_token},
                    {"$set": {"username": username}}
                )
                res.set_status(200, "OK")
                res.text("Change Successfully")
                handler.request.sendall(res.to_data())
            elif validate_password(password):
                hash_pwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                user_collection.update_one(
                    {"auth_token": hash_token},
                    {"$set": {"username": username, "password": hash_pwd}}
                )
                res.set_status(200, "OK")
                res.text("Change Successfully")
                handler.request.sendall(res.to_data())
            else:
                res.set_status(400, "Invalid")
                res.text("Invalid Password")
                handler.request.sendall(res.to_data())
    else:
        res.set_status(400, "Invalid")
        res.text("Invalid Password")
        handler.request.sendall(res.to_data())