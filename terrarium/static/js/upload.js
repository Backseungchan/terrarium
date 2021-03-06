function getCookie(cName) {
  cName = cName + "=";
  var cookieData = document.cookie;
  var start = cookieData.indexOf(cName);
  var cValue = "";
  if (start != -1) {
    start += cName.length;
    var end = cookieData.indexOf(";", start);
    if (end == -1) end = cookieData.length;
    cValue = cookieData.substring(start, end);
  }
  return unescape(cValue);
}

// 이미지 업로드시 썸네일 형식으로 비쳐줌
function setThumbnail(event) {
  bsCustomFileInput.init();
  var reader = new FileReader();

  reader.onload = function (event) {
    style =
      "background-image: url(" +
      event.target.result +
      "),url(../static/images/noImage.gif);";
    document.querySelector("#thumbnailBox").setAttribute("style", style);
  };

  reader.readAsDataURL(event.target.files[0]);
}

// 취소 버튼
function cancel(category) {
  window.location.href("../list/" + category);
}

// 완료 버튼
function posting(category) {
  let title = $("#title").val();
  let pic = $("#pic")[0].files[0];
  let contents = $("#contents").val();
  let uid = getCookie("uid");

  let form_data = new FormData();
  form_data.append("uid", uid);
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
