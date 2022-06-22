function updateButton(postnum, category, uid) {
  location.href =
    "../updatepage" +
    "?category=" +
    category +
    "&postnum=" +
    postnum +
    "&uid=" +
    uid;
}

function myPage(uid) {
  location.href = "../mypage?uid=" + uid;
}

function goBack(uid) {
  location.href = "../?uid=" + uid;
}

function uploadButton(category, uid) {
  location.href = "../uploadpage?uid=" + uid + "&category=" + category;
}
