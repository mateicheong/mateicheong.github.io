(() => {
  // <stdin>
  var header = document.getElementsByTagName("header")[0];
  var dropDownMenus = document.querySelectorAll("header .pure-menu-children");
  var threshold = 100;
  var lastScrollY = window.scrollY;
  var isScrollHide = false;
  var isInDropdownMenu = false;
  var headerHeight = header !== void 0 ? header.offsetHeight : 0;
  function updateNavbarVisibility() {
    if (isMouseNearTop || !isScrollHide || isInDropdownMenu) {
      header.classList.remove("hide");
    } else {
      header.classList.add("hide");
    }
  }
  function throttle(fn, wait) {
    let lastTime = 0;
    return function(...args) {
      const now = Date.now();
      if (now - lastTime >= wait) {
        lastTime = now;
        fn.apply(this, args);
      }
    };
  }
  window.addEventListener("scroll", throttle(() => {
    if (!header) {
      return;
    }
    const currentScrollY = window.scrollY;
    if (Math.abs(currentScrollY - lastScrollY) < threshold) {
      return;
    }
    if (currentScrollY > lastScrollY && currentScrollY > 100) {
      isScrollHide = true;
    } else {
      isScrollHide = false;
    }
    lastScrollY = currentScrollY;
    updateNavbarVisibility();
  }, 50));
  window.addEventListener("resize", () => {
    headerHeight = header.offsetHeight;
  });
  window.addEventListener("mousemove", throttle((e) => {
    isMouseNearTop = e.clientY <= headerHeight;
    updateNavbarVisibility();
  }, 50));
  for (const menu of dropDownMenus) {
    menu.addEventListener("mousemove", () => {
      isInDropdownMenu = true;
      updateNavbarVisibility();
    });
    menu.addEventListener("mouseleave", () => {
      isInDropdownMenu = false;
      updateNavbarVisibility();
    });
  }
})();
