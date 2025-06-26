(async () => {
  const get_captcha = () => {
    return document.querySelector(".captcha-wrapper .captcha-img").src.split("/").pop().split(".")[0];
  };
  const update_captcha = () => {
    document.querySelector(".captcha-wrapper .captcha-refresh").click();
    console.log(`Click!`);
  };
  const append_to_pwd = (text) => {
    const pw = document.querySelector('.password-box [contenteditable="true"]');
    pw.appendChild(document.createTextNode(text));
  };
  let captcha = get_captcha();
  while (/\d/.test(captcha)) {
    update_captcha();
    await new Promise(r => setTimeout(r, 750));
    captcha = get_captcha();
  }
  console.log("🎯 Captcha has no digits!: " + captcha);
  append_to_pwd(captcha);
})();