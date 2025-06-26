(async () => {
  const get_captcha = () => {
    return document.querySelector(".captcha-wrapper .captcha-img").src.split("/").pop().split(".")[0];
  };
  const update_captcha = () => {
    document.querySelector(".captcha-wrapper .captcha-refresh").click();
    console.log(`Click!`);
  };
  const append_to_pwd = (html) => {
    const pw = document.querySelector('.password-box [contenteditable="true"]');
    pw.insertAdjacentHTML('beforeend', html);
  };
  const format_bold_italic = (txt) => {
    let result = "";
    const vowels = /[aeiouyAEIOUY]/;
    for (const char of txt) {
      if (vowels.test(char)) {
        result += `<strong>${char}</strong>`;
      } else {
        result += `<em>${char}</em>`;
      }
    }
    return result;
  };
  let captcha = get_captcha();
  while (/\d/.test(captcha)) {
    update_captcha();
    await new Promise(r => setTimeout(r, 750));
    captcha = get_captcha();
  }
  console.log("🎯 Captcha has no digits!: " + captcha);
  append_to_pwd(format_bold_italic(captcha));
})();