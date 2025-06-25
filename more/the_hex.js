(async () => {
  const to_hex = (rgb_str) => {
    const [r, g, b] = rgb_str.match(/\d+/g).map(Number);
    return "#" + [r, g, b].map(x => x.toString(16).padStart(2, "0")).join("");
  };

  while (true) {
    const el = document.querySelector(".hex .rand-color");
    const bg = getComputedStyle(el).backgroundColor;
    const hex = to_hex(bg);

    console.log(`Current color: ${hex}`);

    if (!/\d/.test(hex)) break;

    document.querySelector(".hex .refresh").click();
    await new Promise(r => setTimeout(r, 50));
  }

  console.log("🎯 Hex color has no digits!");
})();