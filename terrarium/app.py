import datetime

from flask import Flask, render_template, request, jsonify
from static.sampledata import posts
import certifi
from pymongo import MongoClient
import hashlib
import jwt

app = Flask(__name__)

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.cdgld5e.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
# client = MongoClient('mongodb+srv://test:sparta@cluster0.ihwyd.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.terrarium

SECRET_KEY = 'SPARTA'

pwconfirmed = False
# uid = "asd"

# TODO: 모든 목록 페이지에 대해 페이지네이션을 위해 데이터 끊기가 필요함.
# TODO: imhjnoh가 작성한 내용에서 댓글의 경우 유저아이디를 uid, 포스트의 경우 ID 로 작업했기 때문에 통일 필요.

@app.route('/')
def main():
    return render_template("index.html")


@app.route('/detail')
def detail():
    return render_template("detail.html")


# TODO: 패스워드가 확인되지 않아도 주소를 입력하면 들어가짐
@app.route('/mypage')
def mypage_pw():
    uid = request.args.get("uid")
    print(uid)
    return render_template("mypage.html", page="mypage_pwconfirm", uid=uid)


@app.route('/pwcheck', methods=['POST'])
def pwcheck():
    print(request)
    uid_receive = request.form["uid_give"]
    password_receive = request.form["password_give"]
    # uid_receive = request.form.get('uid_give', False)
    # password_receive = request.form.get('password_give', False)
    print(uid_receive, password_receive)
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    user = db.users.find_one({"uid":uid_receive}, {"_id":False})
    print(user)
    if password_hash == user["password"]:
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"failed"})
    return jsonify({"status":"none"})


@app.route('/mypage/<page>')
def mypage(page):
    uid = request.args.get("uid")
    data = db.users.find_one({"uid":uid}, {"_id":False})
    print(data)
    # 홈일 경우 최근 작성한 게시글 3개와 최근 작성한 댓글 3개
    if page == "home":
        recent_posts = list(db.posts.find({"uid": uid}, {"_id":False}).limit(3))
        data["recent_posts"] = recent_posts
        # 각 포스트의 replies에서 uid가 일치하는 댓글을 리스트로 가져온다.
        recent_replies = list(db.posts.aggregate([
            {"$match": {"replies.uid": uid}},
            {"$unwind": "$replies"},
            {"$match": {"replies.uid": uid}},
            {"$sort": {"replies.created_at": -1}},
            {"$limit": 3}
        ]))
        data["recent_replies"] = recent_replies
    # 작성한 게시글
    elif page == "posts":
        posts = list(db.posts.find({"uid": uid}, {"_id": False}))
        data["posts"] = posts
    # 작성한 댓글
    elif page == "replies":
        # 각 포스트의 replies에서 uid가 일치하는 댓글을 리스트로 가져온다.
        replies = list(db.posts.aggregate([
            {"$match":{"replies.uid": uid}},
            {"$unwind": "$replies"},
            {"$match":{"replies.uid": uid}},
            {"$sort": {"replies.created_at": -1}},
        ]))
        data["replies"] = replies
    elif page == "/":
        page = "mypage_pwconfirm"

    print(data)
    return render_template("mypage.html", page=page, data=data, uid=uid)


# 회원 탈퇴 기능
@app.route('/quit', methods=["POST"])
def quit():
    uid = request.form["id_give"]
    # 유저 데이터에 is_quit 인자를 추가해서 soft delete.
    # TODO: 로그인 기능에서도 is_quit 인자가 있는지, 변수가 1인지 검사하고 로그인 통과시켜야 합니다.
    db.users.update_one({"uid":uid}, {"$set": {"is_quit": 1}})
    return jsonify({"status":"success"})


# 비밀번호 변경 기능
@app.route('/mypage/pwchange', methods=["POST"])
def pwchange():
    uid = request.form["id_give"]
    pw = request.form["password_give"]
    password_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    print(password_hash)
    db.users.update_one({"uid": uid}, {"$set": {"password": password_hash}})
    return jsonify({"status":"success"})


@app.route('/reply_sample')
def reply_sample():
    # TODO : 기능 확인을 위해 댓글 페이지를 따로 뺐으나 포스트 상세 페이지 쪽으로 해당 api의 위치를 옮겨야 함.
    # 임시로 uid와 postnum를 받아오는 곳이 있지만 Post 상세 페이지에서 사용할 경우 해당 페이지의 uid와 postnum을 사용하면 됨.
    uid = request.args.get("uid")
    postnum = int(request.args.get("postnum"))

    # TODO : 상세 페에지에서 불러오는 포스트 내용으로 아래 replies 를 대체할 수 있으며, 대체해야 한다.
    replies = db.posts.find_one({"postnum": postnum}, {"_id":False})

    # 만약 해당 포스트에 댓글이 없다면, 댓글 목록(replies_list)를 빈 리스트로 넘긴다. None으로 넘길 시 오류 발생.
    if "replies" in replies:
        replies_list = list(replies["replies"])
    elif len(list(replies["replies"])) == 0:
        replies_list = []
    else:
        replies_list = []

    return render_template("reply_sample.html", replies=replies_list, postnum=postnum, uid=uid)


# 댓글 작성 기능
@app.route('/reply', methods=['POST'])
def reply_post():
    # 클라이언트로부터 댓글 작성 데이터 수집
    postnum_receive = int(request.form['postnum_give'])
    uid_receive = request.form['uid_give']
    name_receive = db.users.find_one({"uid":uid_receive}, {"_id":False})["nickname"]
    text_receive = request.form['text_give']

    # replynum 결정. 댓글이 없다면 0, 있다면 마지막 댓글의 replynum에 +1
    a_post = db.posts.find_one({"postnum": postnum_receive}, {"_id":False})
    if "replies" in a_post:
        # replies_num = len(list(db.posts.find_one({"postnum": postnum_receive}, {"_id": False})["replies"]))
        # replies_num = int(db.posts.aggregate([{"$addFields": {"lastElem": {"$last": "$replies"}}}])["replynum"])
        if "replies" in a_post:
            lastone = list(a_post["replies"]).pop()
            replies_num = lastone["replynum"]
        elif len(list(a_post["replies"])) == 0:
            replies_num = 0
        else:
            replies_num = 0
    else:
        replies_num = 0

    # 완성된 데이터
    data = {
        'uid': uid_receive,
        "name": name_receive,
        "text": text_receive,
        "replynum": int(replies_num + 1),
        "created_at": datetime.datetime.now(),
    }

    # db 업데이트
    # 참고 : post 안의 list에 업데이트 하는 것이기 때문에 $push를 사용하였음.
    db.posts.update_one({"postnum":postnum_receive}, {'$push': {'replies': data}})
    return jsonify({"status":"success"})


# 댓글 삭제 기능
@app.route('/reply/del', methods=['POST'])
def reply_delete():
    # postnum과 replynum을 받아서 삭제 처리한다. 작성과 마찬가지로 오브젝트 안 list이기 때문에 $pull을 사용.
    postnum_receive = int(request.form['postnum_give'])
    replynum_receive = int(request.form['replynum_give'])
    db.posts.update_one({"postnum": postnum_receive}, {'$pull': {'replies': {"replynum" : int(replynum_receive)}}})
    return jsonify({"status":"success"})


# 댓글 수정 기능
@app.route('/reply/update', methods=['POST'])
def reply_update():
    # postnum과 replynum, text를 받아서 수정 처리한다. 작성과 마찬가지로 오브젝트 안 list이기 때문에 $set을 사용.
    postnum_receive = int(request.form['postnum_give'])
    replynum_receive = int(request.form['replynum_give'])
    text_receive = request.form['text_give']
    db.posts.update_one({"postnum": postnum_receive, "replies.replynum":replynum_receive}, {'$set': {"replies.$.text":text_receive}})
    return jsonify({"status":"success"})




if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)
