from flask import Flask, render_template, request, jsonify
from static.sampledata import posts
import certifi
from pymongo import MongoClient

app = Flask(__name__)

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.cdgld5e.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
# client = MongoClient('mongodb+srv://test:sparta@cluster0.ihwyd.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.terrarium

# TODO: 모든 목록 페이지에 대해 페이지네이션을 위해 데이터 끊기가 필요함.
# TODO: imhjnoh가 작성한 내용에서 댓글의 경우 유저아이디를 uid, 포스트의 경우 ID 로 작업했기 때문에 통일 필요.

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
    uid = 17
    data = {}
    if page == "home":
        recent_posts = list(db.posts.find({"ID": uid}, {"_id":False}).limit(3))
        data["recent_posts"] = recent_posts
        recent_replies = list(db.posts.aggregate([
            {"$match": {"replies.uid": uid}},
            {"$unwind": "$replies"},
            {"$match": {"replies.uid": uid}},
            {"$limit": 3}
        ]))
        data["recent_replies"] = recent_replies
    elif page == "posts":
        posts = list(db.posts.find({"ID": uid}, {"_id": False}))
        data["posts"] = posts
    elif page == "replies":
        # replies = list(db.posts.find({"replies": {"$elemMatch": {"uid": uid}}}))
        replies = list(db.posts.aggregate([
            {"$match":{"replies.uid": uid}},
            {"$unwind": "$replies"},
            {"$match":{"replies.uid": uid}}
        ]))
        data["replies"] = replies

    print(data)
    return render_template("mypage.html", page=page, data=data)

@app.route('/reply_sample')
def reply_sample():
    # TODO : 기능 확인을 위해 댓글 페이지를 따로 뺐으나 포스트 상세 페이지 쪽으로 해당 api의 위치를 옮겨야 함.
    uid = 17
    postnum = 3

    # TODO : 상세 페에지에서 불러오는 포스트 내용으로 아래 replies 를 대체할 수 있으며, 대체해야 한다.
    replies = db.posts.find_one({"postnum": postnum}, {"_id":False})

    # 만약 해당 포스트에 댓글이 없다면, 댓글 목록(replies_list)를 빈 리스트로 넘긴다. None으로 넘길 시 오류 발생.
    if "replies" in replies:
        replies_list = list(replies["replies"])
    else:
        replies_list = []

    return render_template("reply_sample.html", replies=replies_list, postnum=postnum, uid=uid)


# 댓글 작성 기능
@app.route('/reply', methods=['POST'])
def reply_post():
    # 클라이언트로부터 댓글 작성 데이터 수집
    postnum_receive = int(request.form['postnum_give'])
    uid_receive = request.form['uid_give']
    name_receive = request.form['name_give']
    text_receive = request.form['text_give']

    # replynum 결정. 댓글이 없다면 0, 있다면 댓글 개수에 +1
    if "replies" in db.posts.find_one({"postnum": postnum_receive}, {"_id":False}):
        replies_num = len(list(db.posts.find_one({"postnum": postnum_receive}, {"_id": False})["replies"]))
    else:
        replies_num = 0

    # 완성된 데이터
    data = {
        'uid': int(uid_receive),
        "name": name_receive,
        "text": text_receive,
        "replynum": int(replies_num + 1)
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
