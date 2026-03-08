from util.response import Response
from util.database import chat_collection
import json
import uuid
from util.database import user_collection
import hashlib

def get_authenticated_user(request):
    auth_token = request.cookies.get("auth_token")
    if auth_token is not None:
        hash_token = hashlib.sha256(auth_token.encode()).hexdigest()
        user = user_collection.find_one({"auth_token": hash_token})
        if user is not None:
            return user
    return None

def escape_html(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def create_chat(request, handler):
    res = Response()
    body = request.body.decode()
    message = json.loads(body)["content"]
    user = get_authenticated_user(request)
    if user is not None:
        username = user["username"]
    else:
        session = request.cookies.get("session")
        if session is None:
            session = str(uuid.uuid4())
            res.cookies({"session": session})
        username = session

    chat_collection.insert_one({
        "author": username,
        "id": str(uuid.uuid4()),
        "updated": False,
        "content": message
    })

    res.text("Message Sent")
    res.set_status(200, "OK")
    handler.request.sendall(res.to_data())

def get_chat(request, handler):
    all_data = chat_collection.find({})
    get_data = []
    for data in all_data:
        author = data["author"]
        id = data["id"]
        updated = data["updated"]
        content = escape_html(data["content"])
        reaction = data.get("reactions", {})

        data_dict = {
            "author": author,
            "id": id,
            "updated": updated,
            "content": content,
            "reactions": reaction
        }
        get_data.append(data_dict)
    res = Response()
    res.json({"messages": get_data})
    handler.request.sendall(res.to_data())

def update_chat(request, handler):
    res = Response()
    id = request.path[len("/api/chats/"):]
    data = chat_collection.find_one({"id": id})
    user = get_authenticated_user(request)
    if user is not None:
        username = user["username"]
    else:
        username = request.cookies.get("session")

    if data["author"] != username or username is None:
        res.set_status(403, "Forbidden")
        handler.request.sendall(res.to_data())
        return

    body = request.body.decode()
    body_json = json.loads(body)
    update_content = body_json["content"]

    chat_collection.update_one(
        {"id": id},
        {"$set": {
            "content": update_content,
            "updated": True
        }
    })
    handler.request.sendall(res.to_data())

def delete_chat(request, handler):
    res = Response()
    id = request.path[len("/api/chats/"):]
    data = chat_collection.find_one({"id": id})
    user = get_authenticated_user(request)
    if user is not None:
        username = user["username"]
    else:
        username = request.cookies.get("session")

    if data["author"] != username:
        res.set_status(403, "Forbidden")
        handler.request.sendall(res.to_data())
        return

    chat_collection.delete_one({"id": id})
    handler.request.sendall(res.to_data())

def add_reaction(request, handler):
    res = Response()
    id = request.path[len("/api/reaction/"):]
    data = chat_collection.find_one({"id": id})
    body = request.body.decode()
    body_json = json.loads(body)
    emoji = body_json["emoji"]
    reaction = data.get("reactions")

    user = get_authenticated_user(request)
    if user is not None:
        username = user["username"]
    else:
        username = request.cookies.get("session")

    if reaction is None:
        reaction = {}
    if emoji not in reaction:
        reaction[emoji] = []
    if username in reaction[emoji]:
        res.set_status(403, "Forbidden")
        handler.request.sendall(res.to_data())
        return

    reaction[emoji].append(username)
    chat_collection.update_one(
        {"id": id},
        {"$set": {"reactions": reaction}}
    )

    handler.request.sendall(res.to_data())

def delete_reaction(request, handler):
    res = Response()
    id = request.path[len("/api/reaction/"):]
    data = chat_collection.find_one({"id": id})

    body = request.body.decode()
    body_json = json.loads(body)
    emoji = body_json["emoji"]
    reaction = data.get("reactions")

    user = get_authenticated_user(request)
    if user is not None:
        username = user["username"]
    else:
        username = request.cookies.get("session")

    if username not in reaction[emoji]:
        res.set_status(403,"Forbidden")
        handler.request.sendall(res.to_data())
        return

    reaction[emoji].remove(username)
    if len(reaction[emoji]) == 0:
        del reaction[emoji]

    chat_collection.update_one(
        {"id": id},
        {"$set": {"reactions": reaction}}
    )

    handler.request.sendall(res.to_data())