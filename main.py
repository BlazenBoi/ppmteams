import subprocess
try:
    import asyncio, motor, random, string, math, configparser
    from quart import Quart, request, redirect, url_for, session, send_file, websocket, render_template, jsonify
    from quart_cors import route_cors, cors
    from urllib.parse import urlparse
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import MongoClient
    from datetime import datetime
    import bson.objectid as objectid
    from analytics import analytics as runanalytics
except:
    subprocess.run(["python3", "-m", "pip", "install", "-r", "requirements.txt"])
    import asyncio, motor, random, string, math, configparser
    from quart import Quart, request, redirect, url_for, session, send_file, websocket, render_template, jsonify
    from quart_cors import route_cors, cors
    from urllib.parse import urlparse
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import MongoClient
    from datetime import datetime
    import bson.objectid as objectid
    from analytics import analytics as runanalytics

config = configparser.ConfigParser()
config.read('config.properties')

loop = asyncio.get_event_loop()
app = Quart('', template_folder='templates', static_folder='templates/static')
app = cors(app, allow_origin="*")
app.db = AsyncIOMotorClient(config.get("variables", "mongourl"))[config.get("variables", "database")]
app.mdb = MongoClient(config.get("variables", "mongourl"))[config.get("variables", "database")]
app.db.pcollection = app.db["ppms"]
app.db.acollection = app.db["analytics"]
app.mdb.pcollection = app.mdb["ppms"]

distances = ["Select a Distance", "2", "3","4","5","6","8"]
teams = ["Kachiggas", "Winter Soldiers", "Suckaz"]
t1members = ["Caden Leonard", "Ryan Van de Berghe", "Blake Bullard", "Ryan Krazinski", "Grant Norgart", "Claudio Auns", "Jett Jones", "John Adam Kieda", "Hudson Lowry", "Damian Garza", "Aarman Dillon", "Quentin Gordon"]
t2members = ["Jude Alvarez", "Griffin Cords", "Carter Haskell", "Caleb Lo", "Dylan Torres", "Adhavan Palanivelrajan", "Gavin Folkerts", "Grayson Schick", "James Mason", "Jack Gassett", "Arnav Kakarala", "Drew Collett"]
t3members = ["Zach Troutman", "Michael Fuller", "Alex Severson", "Michael Kovach", "Jason Mccarthy", "Rohan Kumar", "Jack Swadish", "Ethan Bowen", "Colin Van de Berghe", "Momin Haq", "Evan O'Donnell", "Nikhel Kamalia"]
names = ["Select a Runner"] + t1members + t2members + t3members

rawppms = []
for ppm in app.mdb.pcollection.find({}).sort("ppmdate", -1):
    rawppms += [ppm["ppmname"]]
ppms = ["Select a PPM"] + rawppms

@app.route('/', methods=["GET"])
async def home():
    thisppms = []
    for ppm in await getrawppms(False):
        cfound = await app.db.pcollection.find_one({"ppmname":ppm})
        dbppmtimes = cfound["ppmtimes"]
        ppmtimes = []
        t1 = {"team":teams[0], "score":0, "runners":0, "allin":"false"}
        t2 = {"team":teams[1], "score":0, "runners":0, "allin":"false"}
        t3 = {"team":teams[2], "score":0, "runners":0, "allin":"false"}
        placement = 0
        hasbeentied = False
        tiedadd = 0
        tiedadd2 = False
        tiedtime = 0
        for ppmtime in dbppmtimes:
            #if placement == 0 and ppmtime["tied"] == True:
                #placement = 1
            if ppmtime["tied"] == False:
                tiedtime = 0
                if hasbeentied == True:
                    placement += tiedadd
                    hasbeentied = False
                    tiedadd = 0
                    if tiedadd2 == True:
                        placement += 1
                    else:
                        placement += 1
                else:
                    if tiedtime == ppmtime["conversionint"] or tiedtime == 0:
                        if hasbeentied == False:
                            placement += 1
                        tiedtime = ppmtime["conversionint"]
                        tiedadd += 1
                        hasbeentied = True
                    else:
                        tiedtime = 0
                        if hasbeentied == True:
                            placement += tiedadd
                            hasbeentied = True
                            tiedadd = 0
                            tiedadd2 = True
            team = None
            if ppmtime["name"] in t1members:
                team = teams[0]
                if t1["runners"] < 5:
                    t1["score"] += placement
                    t1["runners"] += 1
            if ppmtime["name"] in t2members:
                team = teams[1]
                if t2["runners"] < 5:
                    t2["score"] += placement
                    t2["runners"] += 1
            if ppmtime["name"] in t3members:
                team = teams[2]
                if t3["runners"] < 5:
                    t3["score"] += placement
                    t3["runners"] += 1
            if t1["runners"] >= 5:
                t1["allin"] = "true"
            if t2["runners"] >= 5:
                t2["allin"] = "true"
            if t3["runners"] >= 5:
                t3["allin"] = "true"
            ppmtimes.append({"place":placement, "name":ppmtime["name"], "team":team, "time":ppmtime["time"], "distance":int(ppmtime["distance"]), "conversionstr":ppmtime["conversionstr"], "conversionint":int(ppmtime["conversionint"]), "converted":ppmtime["converted"], "tied":ppmtime["tied"]})
        placements = [t1, t2, t3]
        placements = sorted(placements, key=lambda x: x['runners'], reverse=True)
        placements = sorted(placements, key=lambda x: x['score'])
        thisppms.append({"ppm":ppm, "runners":ppmtimes, "placements":placements})
    thisrawppms = await getheader(None)
    return await render_template("main.html", oppms=thisrawppms, ppms=thisppms)

@app.route('/ppm/<ppm>', methods=["GET", "POST"])
async def homeppm(ppm):
    thisppms = []
    cfound = await app.db.pcollection.find_one({"ppmname":ppm})
    dbppmtimes = cfound["ppmtimes"]
    ppmtimes = []
    t1 = {"team":teams[0], "score":0, "runners":0, "allin":"false"}
    t2 = {"team":teams[1], "score":0, "runners":0, "allin":"false"}
    t3 = {"team":teams[2], "score":0, "runners":0, "allin":"false"}
    placement = 0
    hasbeentied = False
    tiedadd = 0
    for ppmtime in dbppmtimes:
        if placement == 0 and ppmtime["tied"] == True:
            placement = 1
        else:
            if ppmtime["tied"] == False:
                if hasbeentied == True:
                    placement += tiedadd
                    hasbeentied = False
                    tiedadd = 0
                else:
                    placement += 1
            else:
                if hasbeentied == False:
                    placement += 1
                tiedadd += 1
                hasbeentied = True
                team = None
                if ppmtime["name"] in t1members:
                    team = teams[0]
                    if t1["runners"] < 5:
                        t1["score"] += placement
                        t1["runners"] += 1
                    else:
                        t1["allin"] = "true"
                if ppmtime["name"] in t2members:
                    team = teams[1]
                    if t2["runners"] < 5:
                        t2["score"] += placement
                        t2["runners"] += 1
                    else:
                        t2["allin"] = "true"
                if ppmtime["name"] in t3members:
                    team = teams[2]
                    if t3["runners"] < 5:
                        t3["score"] += placement
                        t3["runners"] += 1
                    else:
                        t3["allin"] = "true"
                ppmtimes.append({"place":placement, "name":ppmtime["name"], "team":team, "time":ppmtime["time"], "distance":int(ppmtime["distance"]), "conversionstr":ppmtime["conversionstr"], "conversionint":int(ppmtime["conversionint"]), "converted":ppmtime["converted"], "tied":ppmtime["tied"]})
        placements = [t1, t2, t3]
        placements = sorted(placements, key=lambda x: x['runners'], reverse=True)
        placements = sorted(placements, key=lambda x: x['score'])
        thisppms.append({"ppm":ppm, "runners":ppmtimes, "placements":placements})
        thisrawppms = await getheader(ppm)
        return await render_template("main.html", oppms=thisrawppms, ppms=thisppms)

@app.route("/totals")
async def totals():
    return None

@app.route("/newppm", methods=["GET", "POST"])
async def newppm():
    if request.method == "GET":
        return await render_template("newppm.html")
    else:
        form = await request.form
        ppmname = form["ppmname"]
        ppmdate = form["ppmdate"]
        ppmdatetime = datetime.strptime(ppmdate, '%Y-%m-%d')
        ppmtype = form["ppmtype"]
        scores = [{"teamname":teams[0], "score":0, "runners":0}, {"teamname":teams[1], "score":0, "runners":0}, {"teamname":teams[2], "score":0, "runners":0}]
        await app.db.pcollection.insert_one({"ppmname":ppmname, "ppmdate":ppmdatetime, "ppmtype":ppmtype, "ppmtimes":[], "scores":scores})
        return redirect(url_for("home"))

@app.route('/submit', methods=["GET", "POST"])
async def submit():
    if request.method == "GET":
        return await render_template("submit.html", names=names, ppms=await getrawppms(True), distances=distances, failed="")
    else:
        collection = app.db["ppmteams"]
        form = await request.form
        conversion = None
        convertdistance = int(form["distance"])
        if "LPPM" in form["ppm"]:
            convertdistance = 8
        elif "SPPM" in form["ppm"]:
            convertdistance = 4
        conversion = await convert(int(form["distance"]), convertdistance, form["time"])
        conversionint = conversion[0]
        conversionstr = conversion[1]
        converted = conversion[2]
        if converted == True:
            conversionstr += "*"
        cfound = await app.db.pcollection.find_one({"ppmname":form["ppm"]})
        dbppmtimes = cfound["ppmtimes"]
        ppmtimes = []
        for ppmtime in dbppmtimes:
            ppmtimes.append({"name":ppmtime["name"], "time":ppmtime["time"], "distance":int(ppmtime["distance"]), "conversionstr":ppmtime["conversionstr"], "conversionint":int(ppmtime["conversionint"]), "converted":ppmtime["converted"], "tied":ppmtime["tied"]})
        ppmtimes.append({"name":form["fname"], "time":form["time"], "distance":int(form["distance"]), "conversionstr":conversionstr, "conversionint":int(conversionint), "converted":converted, "tied":False})
        scores = cfound["scores"]
        ppmtimes = sorted(ppmtimes, key=lambda x: x['distance'], reverse=True)
        ppmtimes = sorted(ppmtimes, key=lambda x: x['conversionint'])
        await app.db.pcollection.update_one({"ppmname":form["ppm"]}, {"$set":{"ppmtimes":ppmtimes, "scores":scores}})
        #await collection.insert_one({"ppm":form["ppm"], "name":form["fname"], "time":form["time"], "distance":form["distance"], "conversionstr":conversionstr, "conversionint":conversionint, "converted":converted})
        return redirect(url_for("submit") + "/" + form["ppm"])

@app.route('/submit/<ppm>', methods=["GET", "POST"])
async def submitppm(ppm):
    if request.method == "GET":
        defaultdistance = None
        if "LPPM" in ppm:
            defaultdistance = "6"
        elif "SPPM" in ppm:
            defaultdistance = "4"
        thisnames = names.copy()
        cfound = await app.db.pcollection.find_one({"ppmname":ppm})
        dbppmtimes = cfound["ppmtimes"]
        for name in dbppmtimes:
            thisnames.remove(name["name"])
        return await render_template("submit.html", names=thisnames, ppms=[ppm], distances=distances, defaultdistance=defaultdistance, failed="")
    else:
        return redirect(url_for("submit"))

@app.route("/analytics", methods=["POST"])
async def analytics():
    if config.get("config", "analytics") == "true":
        json = await request.get_json()
        await runanalytics(json, app)
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failure"})

@app.route("/js/analytics")
async def jsanalytics():
    return await send_file("./templates/static/analytics.js", mimetype="text/javascript")

async def convert(startdistance, enddistance, time):
    if startdistance == enddistance:
        splittime = time.split(":")
        seconds = int(splittime[0])*60 + int(splittime[1])
        return [seconds, time, False]
    splittime = time.split(":")
    seconds = int(splittime[0])*60 + int(splittime[1])
    if enddistance == 4:
        if startdistance == 2:
            seconds = (seconds * (enddistance/startdistance)) + 180
        if startdistance == 3:
            seconds = (seconds * (enddistance/startdistance)) + 20
        fminutes = math.floor(seconds/60)
        fseconds = round(seconds - (fminutes * 60))
        if fseconds < 10:
            ftime = str(fminutes) + ":0" + str(fseconds)
        else:
            ftime = str(fminutes) + ":" + str(fseconds)
    elif enddistance == 8:
        if startdistance == 2:
            seconds = (seconds * (enddistance/startdistance)) + 360
        if startdistance == 3:
            seconds = (seconds * (enddistance/startdistance)) + 180
        elif startdistance == 4:
            seconds = (seconds * (enddistance/startdistance)) + 120
        elif startdistance == 5:
            seconds = (seconds * (enddistance/startdistance)) + 80
        elif startdistance == 6:
            seconds = (seconds * (enddistance/startdistance)) + 40
        fminutes = math.floor(seconds/60)
        fseconds = round(seconds - (fminutes * 60))
        if fseconds < 10:
            ftime = str(fminutes) + ":0" + str(fseconds)
        else:
            ftime = str(fminutes) + ":" + str(fseconds)
    return [seconds, ftime, True]

async def getrawppms(add):
    thisraw = ["Select a PPM"]
    thisraw2 = []
    for ppm in await app.db.pcollection.find({}).sort("ppmdate", -1).to_list(None):
        thisraw += [ppm["ppmname"]]
        thisraw2 += [ppm["ppmname"]]
    if add == True:
        return thisraw
    elif add == False:
        return thisraw2

async def getheader(active):
    thisraw = []
    for ppm in await app.db.pcollection.find({}).sort("ppmdate", -1).to_list(None):
        if datetime.now() > ppm["ppmdate"]:
            thisraw += [ppm["ppmname"]]
    thisrawppms = []
    if active == None:
        thisrawppms.append({"ppm":"Show All", "active":"true"})
        for tppm in thisraw:
            thisrawppms.append({"ppm":tppm, "active":"false"})
    else:
        thisrawppms.append({"ppm":"Show All", "active":"false"})
        for tppm in thisraw:
            if tppm == active:
                thisrawppms.append({"ppm":tppm, "active":"true"})
            else:
                thisrawppms.append({"ppm":tppm, "active":"false"})
    return thisrawppms