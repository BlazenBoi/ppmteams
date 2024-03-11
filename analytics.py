import random, string

async def newdid(app):
    validnewid = False
    while validnewid == False:
        newid = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        collectionfound = await app.db.acollection.find_one({"did":newid})
        if collectionfound == None:
            validnewid = True
    return newid

async def analytics(json, app):
    dstr = ""
    for thing in json:
        dstr += str(json[thing])
    dfound = await app.db.acollection.find_one({"dstr":dstr})
    if dfound == None:
        await app.db.acollection.insert_one({"dstr":dstr, "did":await newdid(app), "total":0})
        await app.db.acollection.update_one({"dstr":dstr}, {"$set":{"total":1}})
    else:
        await app.db.acollection.update_one({"dstr":dstr}, {"$set":{"total":dfound["total"] + 1}})