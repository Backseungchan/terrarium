function updateButton(postnum, category) {
  location.href =
    "../updatepage" + "?category=" + category + "&postnum=" + postnum;
}

function deleteButton(postnum) {
  location.href =
    "../updatepage" + "?category=" + category + "&postnum=" + postnum;
}

function myPage() {
  location.href = "../mypage";
}

function goBack() {
  location.href = "../";
}

function uploadButton(category, uid) {
  location.href = "../uploadpage?category=" + category;
}
