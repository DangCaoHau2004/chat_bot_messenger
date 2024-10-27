(function (d, s, id) {
  var js,
    fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) {
    return;
  }
  js = d.createElement(s);
  js.id = id;
  js.src = "//connect.facebook.net/en_US/messenger.Extensions.js";
  fjs.parentNode.insertBefore(js, fjs);
})(document, "script", "Messenger");
alert("hello");
window.extAsyncInit = function () {
  // the Messenger Extensions JS SDK is done loading
  MessengerExtensions.getContext(
    "773997401470202",
    function success(thread_context) {
      document.getElementById("psid").value = thread_context.psid;
      handleClickButtonOrder();
    },
    function error(err) {
      console.log("Lỗi đặt hàng: ", err);
    }
  );
};

function checkValidate() {
  let ten = document.getElementById("name").value;
  let sdt = document.getElementById("sdt").value;
  let diachi = document.getElementById("adress").value;
  if (ten !== "" && sdt.match(/^0\d{9}$/) && diachi != "") {
    return true;
  }
  return false;
}
function handleClickButtonOrder() {
  const orderButton = document.getElementById("Order");
  orderButton.addEventListener("click", function (event) {
    let checkValidate = checkValidate();
    const data = {
      psid: document.getElementById("psid").value,
      ten: document.getElementById("name").value,
      sdt: document.getElementById("sdt").value,
      diachi: document.getElementById("adress").value,
    };
    const url = `${window.location.origin}/handle-order`;
    if (checkValidate) {
      console.log(data);

      MessengerExtensions.requestCloseBrowser(
        function success() {
          // webview closed
        },
        function error(err) {
          console.log(err);
        }
      );
      fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          console.log(data);
        })
        .catch((error) => {
          console.log(error);
        });
    } else {
      console.log("Dữ liệu không hợp lệ!");
    }
  });
}
