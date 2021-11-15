# For flask implementation
from flask import Flask, render_template, request, redirect, url_for
from pymongo import ASCENDING, DESCENDING, MongoClient  # Database connector
from bson.objectid import ObjectId  # For ObjectId to work
from bson.errors import InvalidId  # For catching InvalidId exception for ObjectId
import random
from datetime import datetime

import os

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
# Configure the connection to the database
client = MongoClient(mongodb_host, mongodb_port)
db = client.camp2016  # Select the database
todos = db.todo  # Select the collection

app = Flask(__name__)
title = "Swish 6kr Jonas lol"
heading = "Swish 6kr Jonas lol"
# modify=ObjectId()


def redirect_url():
    return request.args.get('next') or \
        request.referrer or \
        url_for('index')


@app.route("/")
@app.route("/list")
def lists():
    # Display the all Tasks
    todos_l = todos.find().sort("date", ASCENDING)
    todos_random = list(todos.find({'done': 'no'}))
    random.shuffle(todos_random)
    next_receiver_index = random.randint(0, len(todos_random))
    a1 = "active"
    top_list = top(3)
    tally = todos.count()
    tally_done = todos.find({"done": "yes"}).count()
    tally_left = todos.find({"done": "no"}).count()
    price_incoming = 6

    price_outgoing = 56
    completed_donors = todos.find({'done': 'yes'}).distinct('name')
    incomplete_donations = todos.find({'done': 'no'}).sort(
        "date", ASCENDING).distinct('name')
    incomplete_donors = [
        donor for donor in incomplete_donations if donor not in completed_donors]
    if(len(incomplete_donors) > 0):
        next_donor_name = incomplete_donors[0]
    else:
        if(len(incomplete_donations) > 0):
            next_donor_name = incomplete_donations[0]
        else:
            next_donor_name = "The list is empty!"
    next_donor_id = todos.find({'done': 'no'}, {'name': next_donor_name}).sort(
        "date", ASCENDING)
    if(next_donor_id.count() > 0):
        next_donor_id = next_donor_id[0]['_id']
    else:
        next_donor_id = ""
    return render_template('index.html',
                           a1=a1,
                           todos=todos_l,
                           todos_random=todos_random,
                           t=title,
                           h=heading,
                           top1=top_list[0],
                           top2=top_list[1],
                           top3=top_list[2],
                           tally_done=tally_done,
                           tally_left=tally_left,
                           money_incoming=tally*price_incoming,
                           money_outgoing=tally_done*price_outgoing,
                           next_donor_name=next_donor_name,
                           next_donor_id=next_donor_id,
                           next_receiver_index=next_receiver_index,
                           today=datetime.date(datetime.now())
                           )


def top(depth=3):
    top_list = list(todos.aggregate(
        [{"$sortByCount": "$name"}]))
    # result =
    if(len(top_list) < 3):
        for x in range(len(top_list), 3):
            top_list.append({u'count': 0, u'_id': u'N/A'})

    for element in top_list:
        top_list[top_list.index(element)] = element['_id'] + \
            " (" + str(element['count']) + ")"

    return top_list


@ app.route("/uncompleted")
def tasks():
    # Display the Uncompleted Tasks
    todos_l = todos.find({"done": "no"}).sort("date", ASCENDING)
    a2 = "active"
    return render_template('index.html', a2=a2, todos=todos_l, t=title, h=heading)


@ app.route("/completed")
def completed():
    # Display the Completed Tasks
    todos_l = todos.find({"done": "yes"}).sort("date", ASCENDING)
    a3 = "active"
    return render_template('index.html', a3=a3, todos=todos_l, t=title, h=heading)


@ app.route("/password")
def password_prompt():
    return render_template('password-prompt.html', t=title, h=heading)


@ app.route("/done", methods=['GET', 'POST'])
def done():
    # Done-or-not ICON
    _id = request.values.get("_id")
    password = request.values.get("password")
    if password == "juice":
        task = todos.find({"_id": ObjectId(_id)})
        if(task[0]["done"] == "yes"):
            todos.update({"_id": ObjectId(_id)}, {"$set": {"done": "no"}})
        else:
            todos.update({"_id": ObjectId(_id)}, {"$set": {"done": "yes"}})
        # Re-directed URL i.e. PREVIOUS URL from where it came into this one
        return redirect("./")

    #	if(str(redir)=="http://localhost:5000/search"):
    #		redir+="?key="+id+"&refer="+refer

    else:
        return redirect(url_for('password_prompt', _id=_id))


# @app.route("/add")
# def add():
#	return render_template('add.html',h=heading,t=title)


@ app.route("/action", methods=['POST'])
def action():
    # Adding a Task
    name = request.values.get("name")
    date = request.values.get("date")
    pr = request.values.get("pr")
    password = request.values.get("password")
    if password == "juice":
        todos.insert({"name": name, "date": date, "done": "no"})
    return redirect("/list")


@ app.route("/remove")
def remove():
    # Deleting a Task with various references
    key = request.values.get("_id")
    todos.remove({"_id": ObjectId(key)})
    return redirect("/")


@ app.route("/update")
def update():
    id = request.values.get("_id")
    task = todos.find({"_id": ObjectId(id)})
    return render_template('update.html', tasks=task, h=heading, t=title)


@ app.route("/action3", methods=['POST'])
def action3():
    # Updating a Task with various references
    name = request.values.get("name")
    date = request.values.get("date")
    id = request.values.get("_id")
    done = request.values.get("done")
    submit_action = request.values.get("button")
    password = request.values.get("password")
    if password == "juice":
        if submit_action == "update":
            todos.update({"_id": ObjectId(id)}, {
                         '$set': {"name": name, "date": date, "done": done}})
        if submit_action == "delete":
            todos.remove({"_id": ObjectId(id)})
        return redirect("/")
    return redirect(request.referrer)


@ app.route("/search", methods=['GET'])
def search():
    # Searching a Task with various references

    key = request.values.get("key")
    refer = request.values.get("refer")
    if(refer == "id"):
        try:
            todos_l = todos.find({refer: ObjectId(key)})
            if not todos_l:
                return render_template('index.html', a2=a2, todos=todos_l, t=title, h=heading, error="No such ObjectId is present")
        except InvalidId as err:
            pass
            return render_template('index.html', a2=a2, todos=todos_l, t=title, h=heading, error="Invalid ObjectId format given")
    else:
        todos_l = todos.find({refer: key})
    return render_template('searchlist.html', todos=todos_l, t=title, h=heading)


@ app.route("/about")
def about():
    return render_template('credits.html', t=title, h=heading)


if __name__ == "__main__":
    env = os.environ.get('APP_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    debug = False if env == 'production' else True
    app.run(host='0.0.0.0', port=port, debug=debug)
    # Careful with the debug mode..
