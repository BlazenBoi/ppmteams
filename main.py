import subprocess
try:
    from quart import Quart, jsonify
    from motor.motor_asyncio import AsyncIOMotorClient
    import configparser
except:
    subprocess.run(["python3", "-m", "pip", "install", "-r", "requirements.txt"])
    from quart import Quart, jsonify
    from motor.motor_asyncio import AsyncIOMotorClient
    import configparser

config = configparser.ConfigParser()
config.read('config.properties')

app = Quart(__name__)
app.db = AsyncIOMotorClient(config.get("variables", "mongourl"))[config.get("variables", "database")]
app.db.pcollection = app.db["ppms"]

@app.route("/")
async def hello_world():
    ppms = []
    cursor = app.db.pcollection.find()
    scursor = cursor.sort("ppmdate", 1)
    scursorlist = await scursor.to_list(None)
    for document in scursorlist:
        ppms.append({"ppmname":document["ppmname"], "ppmdate":document["ppmdate"], "ppmtype":document["ppmtype"], "ppmtimes":document["ppmtimes"], "scores":document["scores"]})
    return jsonify(ppms)

    