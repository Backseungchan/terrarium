// 이미지 업로드시 썸네일 형식으로 비쳐줌
function setThumbnail(event) {
  bsCustomFileInput.init();
  var reader = new FileReader();

  reader.onload = function (event) {
    document
      .querySelector("#thumbnail")
      .setAttribute("src", event.target.result);
  };

  reader.readAsDataURL(event.target.files[0]);
}

// 취소 버튼
function cancel() {
  window.location.href("#");
}

// 완료 버튼
function posting(userid, category) {
  let title = $("#title").val();
  let pic = $("#pic")[0].files[0];
  let contents = $("#contents").val();

  let form_data = new FormData();
  form_data.append("userid", userid);
  form_data.append("title", title);
  form_data.append("pic", pic);
  form_data.append("contents", contents);
  form_data.append("category", category);

  $.ajax({
    type: "POST",
    url: "/upload",
    data: form_data,
    cache: false,
    contentType: false,
    processData: false,
    success: function (response) {
      alert(response["msg"]);
      location.href = "./list/" + category; // 완료되면 리스트 항목으로 연결
    },
  });
}
