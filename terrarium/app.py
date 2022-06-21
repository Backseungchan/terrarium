from flask import Flask, render_template, request, jsonify
import json
from static.sampledata import posts, replies
import certifi
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.cdgld5e.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.terrarium


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/detail')
def detail():
    return render_template("detail.html")


@app.route('/mypage')
def mypage_pw():
    return render_template("mypage.html", page="mypage_pwconfirm")


@app.route('/mypage/<page>')
def mypage(page):
    print(json.dumps(posts))
    return render_template("mypage.html", page=page, posts=posts, replies=replies)

@app.route('/reply_sample')
def reply_sample():
    # event_id = "62b18347cfa92ebfb2dbccb5"
    uid = 15
    replies_list = list(db.posts.find_one({"postnum": 1}, {"_id":False})["replies"])
    print(replies_list)
    return render_template("reply_sample.html", replies=replies_list, postnum=1, uid=uid)

@app.route('/reply', methods=['POST'])
def reply_post():
    postnum_receive = int(request.form['postnum_give'])
    uid_receive = request.form['uid_give']
    name_receive = request.form['name_give']
    text_receive = request.form['text_give']
    print(postnum_receive, uid_receive, name_receive, text_receive)
    replies_num = len(list(db.posts.find_one({"postnum": postnum_receive}, {"_id": False})["replies"]))
    print(replies_num)
    data = {
        'uid': uid_receive,
        "name": name_receive,
        "text": text_receive,
        "replynum": str(replies_num + 1)
    }
    db.posts.update_one({"postnum":postnum_receive}, {'$push': {'replies': data}})
    return jsonify({'msg': 'POST(완료) 연결 완료!'})

@app.route('/reply/del', methods=['POST'])
def reply_delete():
    postnum_receive = int(request.form['postnum_give'])
    replynum_receive = int(request.form['replynum_give'])
    print(postnum_receive, replynum_receive)
    db.posts.update_one({"postnum": postnum_receive}, {'$pull': {'replies': {"replynum" : replynum_receive}}})
    return jsonify({'msg': 'POST(완료) 연결 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)
