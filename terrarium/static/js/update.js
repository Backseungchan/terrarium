$(document).ready(function () {
  const URLSearch = new URLSearchParams(location.search);
  let postnum = URLSearch.get("postnum");
  setUp(postnum);
});

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

//기존의 내용 채워두기
function setUp(postnum) {
  $.ajax({
    type: "GET",
    url: "/detail",
    data: { postnum: postnum },
    success: function (response) {
      let post = response["post"];

      let title = post[0]["title"];
      let pic = post[0]["pic"];
      let contents = post[0]["contents"];

      document.querySelector("#title").setAttribute("value", title);
      $(".custom-file-label")[0].innerHTML = pic;
      style =
        "background-image: url(" +
        "../static/pic/" +
        pic +
        "),url(../static/images/noImage.gif);";
      document.querySelector("#thumbnailBox").setAttribute("style", style);

      $("#contents").val(contents);
    },
  });
}

// 이미지 업로드시 썸네일 형식으로 비쳐줌
function setThumbnail(event) {
  bsCustomFileInput.init();
  var reader = new FileReader();

  style =
    "background-image: url(" +
    event.target.result +
    "),url(../static/images/noImage.gif);";
  document.querySelector("#thumbnailBox").setAttribute("style", style);
  reader.readAsDataURL(event.target.files[0]);
}

// 취소 버튼
function cancel() {
  history.back();
}

// 완료 버튼
function fixing() {
  const URLSearch = new URLSearchParams(location.search);
  const category = URLSearch.get("category");
  const postnum = URLSearch.get("postnum");

  let title = $("#title").val();
  let contents = $("#contents").val();
  let pic = $("#pic")[0].files[0];

  console.log(pic);

  let form_data = new FormData();
  form_data.append("postnum", postnum);
  form_data.append("title", title);
  form_data.append("pic", pic);
  form_data.append("contents", contents);

  console.log(form_data);

  $.ajax({
    type: "POST",
    url: "/update",
    data: form_data,
    cache: false,
    contentType: false,
    processData: false,
    success: async function (response) {
      alert(response["msg"]);
      location.href = "../list/" + category;
    },
  });
}
