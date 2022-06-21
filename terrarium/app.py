import certifi
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

ca = certifi.where()  # mongodb 보안 문제로 추가
#승찬님 DB	
client = MongoClient(
    'mongodb+srv://test:sparta@cluster0.m0wkc.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta


@app.route('/')
def main():
    return render_template("update.html")
	# return render_template("upload.html") #테스트를 위한 주석

@app.route("/detail", methods=["GET"])
def get_post():
    postnum_dict = request.args.to_dict() #postnum을 dict형태로 가져옴
	#postnum과 일치하는 post를 db에서 가져옴
    post = list(db.post.find({'postnum': int(postnum_dict["postnum"])}, {'_id': False,}))
    return jsonify({'post': post})

@app.route('/upload', methods=['POST'])
def save_post():
    title = request.form['title']
    contents = request.form['contents']
    category = request.form['category']
    try:
        pic = request.files["pic"]
        filename,extension = pic.filename.split('.')  # 파일의 이름, 확장자
        save_to = f'static/'+pic.filename  # 파일 저장 경로 설정
        pic.save(save_to)  # 파일 저장
    except:
        pic = None

    post_list = list(db.post.find({}, {'_id' : False}))
    postnum = len(post_list) + 1
    doc = {
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
        save_to = f'static/'+pic.filename  # 파일 저장 경로 설정
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)
