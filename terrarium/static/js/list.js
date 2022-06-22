// 페이지가 로드되면 현재 페이지(page)에 따라서 카테고리 표시 상태를 바꾼다.
$(document).ready(function () {});

function updateButton(postnum, category) {
  location.href =
    "../updatepage" + "?category=" + category + "&postnum=" + postnum;
}

function myPage(uid) {
  location.href = "../mypage?uid=" + uid;
}

function goBack() {
  location.href = "../";
}

function uploadButton(category, uid) {
  location.href = "../uploadpage?uid=" + uid;
}
