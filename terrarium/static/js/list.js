function updateButton(postnum, category) {
  location.href =
    "../updatepage" + "?category=" + category + "&postnum=" + postnum;
}

function deleteButton(postnum) {
  $.ajax({
    type: "POST",
    url: "/delete",
    data: {
      postnum: postnum,
    },
    success: function (response) {
      alert(response["msg"]);
      window.location.reload();
    },
  });
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
