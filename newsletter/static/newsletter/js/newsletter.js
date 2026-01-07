(function () {
  function tryOpenModal() {
    if (window.jQuery && $('#newsletterSuccessModal').length) {
      $('#newsletterSuccessModal').modal('show');
      return true;
    }
    return false;
  }

  // Try immediately
  if (tryOpenModal()) return;

  // Retry for up to 1 second (DOM + Django messages)
  let attempts = 0;
  const interval = setInterval(function () {
    attempts++;
    if (tryOpenModal() || attempts > 20) {
      clearInterval(interval);
    }
  }, 50);
})();
