(async () => {
  while (/\d/.test(document.querySelector(".captcha-wrapper .captcha-img").src.split("/").pop())) {
    console.log(`Click!`);
    document.querySelector(".captcha-wrapper .captcha-refresh").click();
    await new Promise(r => setTimeout(r, 750));
  }
})();