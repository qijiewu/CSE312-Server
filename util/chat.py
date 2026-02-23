from util.response import Response
from util.database import chat_collection
import json
import uuid

def escape_html(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text

def create_chat(request, handler):

    res = Response()
    body = request.body.decode()
    message = json.loads(body)["content"]

    session = request.cookies.get("session")
    if session is None:
        session = str(uuid.uuid4())
        res.cookies({"session": session})

    chat_collection.insert_one({
        "author": session,
        "id": str(uuid.uuid4()),
        "updated": False,
        "content": message
    })
    res.text("Message Sent")
    res.set_status(200, "OK")
    handler.request.sendall(res.to_data())

def get_chat(request, handler):

    all_data = chat_collection.find({})
    #({...},{...})
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
    session = request.cookies.get("session")

    if data["author"] != session:
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
    session = request.cookies.get("session")

    if data["author"] != session:
        res.set_status(403, "Forbidden")
        handler.request.sendall(res.to_data())
        return

    chat_collection.delete_one({"id": id})
    handler.request.sendall(res.to_data())

def add_reaction(request, handler):

    res = Response()
    id = request.path[len("/api/reaction/"):]
    data = chat_collection.find_one({"id": id})
    session = request.cookies.get("session")

    body = request.body.decode()
    body_json = json.loads(body)
    emoji = body_json["emoji"]
    reaction = data.get("reactions")
    if reaction is None:
        reaction = {}
    if emoji not in reaction:
        reaction[emoji] = []
    if session in reaction[emoji]:
        res.set_status(403, "Forbidden")
        handler.request.sendall(res.to_data())
        return

    reaction[emoji].append(session)
    chat_collection.update_one(
        {"id": id},
        {"$set": {"reactions": reaction}}
    )

    handler.request.sendall(res.to_data())

def delete_reaction(request, handler):

    res = Response()
    id = request.path[len("/api/reaction/"):]
    data = chat_collection.find_one({"id": id})
    session = request.cookies.get("session")

    body = request.body.decode()
    body_json = json.loads(body)
    emoji = body_json["emoji"]
    reaction = data.get("reactions")

    if session not in reaction[emoji]:
        res.set_status(403,"Forbidden")
        handler.request.sendall(res.to_data())
        return

    reaction[emoji].remove(session)
    if len(reaction[emoji]) == 0:
        del reaction[emoji]

    chat_collection.update_one(
        {"id": id},
        {"$set": {"reactions": reaction}}
    )

    handler.request.sendall(res.to_data())