console.log($("#reply_textarea").val());

function reply_post(postnum, uid) {
  console.log(postnum, uid);
  let text = $("#reply_textarea" + postnum).val();
  if (text == "") {
    alert("댓글 내용을 입력해주세요!");
  } else {
    $.ajax({
      type: "POST",
      url: "/reply",
      data: {
        postnum_give: postnum,
        uid_give: uid,
        name_give: "Sherlock",
        text_give: text,
      },
      success: function (response) {
        alert("등록 완료");
        window.location.reload();
      },
    });
  }
  console.log(text);
}

function reply_delete(replynum, postnum) {
  if (confirm("댓글을 삭제하시겠습니까?")) {
    $.ajax({
      type: "POST",
      url: "/reply/del",
      data: {
        replynum_give: replynum,
        postnum_give: postnum,
      },
      success: function (response) {
        alert("삭제 성공");
        window.location.reload();
      },
    });
  }
}

function reply_toggle_update(replynum, postnum) {
  $("#reply_textarea_update" + postnum + "-" + replynum).toggleClass("d-none");
  $("#reply_text" + postnum + "-" + replynum).toggleClass("d-none");
  $("#reply_delete_button_box" + postnum + "-" + replynum).toggleClass("d-none");
  $("#reply_update_button_box" + postnum + "-" + replynum).toggleClass("d-none");
}

function reply_cancel_update(replynum, postnum) {
  if (confirm("수정을 취소하시겠습니까?")) {
    reply_toggle_update(replynum, postnum);
  }
}

function reply_update(replynum, postnum) {
  let text = $("#reply_update_text" + postnum + "-" + replynum).val();
  if (confirm("댓글을 수정하시겠습니까?")) {
    $.ajax({
      type: "POST",
      url: "/reply/update",
      data: {
        replynum_give: replynum,
        postnum_give: postnum,
        text_give: text,
      },
      success: function (response) {
        alert("수정 성공");
        window.location.reload();
      },
    });
  }
}
