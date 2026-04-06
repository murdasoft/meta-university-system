(function () {
  var list = document.querySelector(".mock-messages");
  if (!list) return;
  setTimeout(function () {
    list.style.opacity = "0";
    list.style.transition = "opacity 0.4s ease";
    setTimeout(function () {
      list.remove();
    }, 450);
  }, 5200);
})();
