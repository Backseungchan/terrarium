from unicodedata import category
import certifi
import json
from pymongo import MongoClient
import jwt
import datetime
import hashlib
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
from static.sampledata import posts, replies

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

ca = certifi.where()  # mongodb 보안 문제로 추가
#승찬님 DB	
# client = MongoClient(
#     'mongodb+srv://test:sparta@cluster0.m0wkc.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
# db = client.dbsparta
#희정님 DB
# client = MongoClient('mongodb+srv://test:sparta@cluster0.cdgld5e.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
# db = client.terrarium
#철호님 DB
client = MongoClient('mongodb+srv://test:sparta@cluster0.ihwyd.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=ca)
db = client.dbsparta

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 문제생기면 여기부터 확인
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 1일 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '존재하지 않는 아이디거나 비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    birthyy_receive = request.form['birthyy_give']
    birthmm_receive = request.form['birthmm_give']
    birthdd_receive = request.form['birthdd_give']
    nickname_receive = request.form['nickname_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "nickname": nickname_receive,  # 닉네임
        "birthyy": birthyy_receive,  # 출생년도
        "birthmm": birthmm_receive,  # 출생월
        "birthdd": birthdd_receive,  # 출생일
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 게시판 C,U
@app.route('/uploadpage')
def load_uploadPage():
    return render_template("uploadpage.html",userid = 'bsc',category = "info")

@app.route('/updatepage')
def load_updatePage():
    return render_template("updatepage.html",userid='bsc')

@app.route("/detail", methods=["GET"])
def get_post():
    postnum_dict = request.args.to_dict() #postnum을 dict형태로 가져옴
	#postnum과 일치하는 post를 db에서 가져옴
    post = list(db.post.find({'postnum': int(postnum_dict["postnum"])}, {'_id': False,}))
    return jsonify({'post': post})

@app.route('/upload', methods=['POST'])
def save_post():
    userid = request.form['userid']
    title = request.form['title']
    contents = request.form['contents']
    category = request.form['category']
    try:
        pic = request.files["pic"]
        filename,extension = pic.filename.split('.')  # 파일의 이름, 확장자
        save_to = f'static/pic/'+pic.filename  # 파일 저장 경로 설정
        pic.save(save_to)  # 파일 저장
    except:
        pic = None

    post_list = list(db.post.find({}, {'_id' : False}))
    postnum = len(post_list) + 1
    doc = {
        'userid':userid,
		'postnum':postnum,
		'category':category,
        'title': title,
        'contents': contents,
    }

    if pic != None:
        doc['pic'] = f'{filename}.{extension}'
    db.post.insert_one(doc)

    return jsonify({'msg': "저장 성공"})

@app.route('/update', methods=['POST'])
def fix_post():
    postnum = request.form['postnum']
    title = request.form['title']
    contents = request.form['contents']
    try:	
        pic = request.files["pic"]
        filename,extension = pic.filename.split('.')  # 파일의 이름, 확장자
        save_to = f'static/pic/'+pic.filename  # 파일 저장 경로 설정
        pic.save(save_to)  # 파일 저장
    except:
        pic = None

    doc = {
        'title': title,
        'contents': contents,
    }

    if pic != None:
        doc['pic'] = f'{filename}.{extension}'
        
    print(doc)
    db.post.update_one({'postnum':int(postnum)}, {'$set':doc})

    return jsonify({'msg': "수정 성공"})

#목록 전체 조회
@app.route('/list/<category>')
def show_list(category):
    category_posts = list(db.post.find({'category': category}, {'_id': False,'category':False}))
    return render_template("list.html", category=category, posts=category_posts, userid='bsc')

#마이페이지
@app.route('/mypage')
def mypage_pw():
    return render_template("mypage.html", page="mypage_pwconfirm")


@app.route('/mypage/<page>')
def mypage(page):
    print(json.dumps(posts))
    return render_template("mypage.html", page=page, posts=posts, replies=replies)


@app.route('/reply_sample')
def reply_sample():
    uid = 15
    replies_list = list(db.posts.find_one({"postnum": 1}, {"_id": False})["replies"])
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
    db.posts.update_one({"postnum": postnum_receive}, {'$push': {'replies': data}})
    return jsonify({'msg': 'POST(완료) 연결 완료!'})


@app.route('/reply/del', methods=['POST'])
def reply_delete():
    postnum_receive = int(request.form['postnum_give'])
    replynum_receive = int(request.form['replynum_give'])
    print(postnum_receive, replynum_receive)
    db.posts.update_one({"postnum": postnum_receive}, {'$pull': {'replies': {"replynum": replynum_receive}}})
    return jsonify({'msg': 'POST(완료) 연결 완료!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)
