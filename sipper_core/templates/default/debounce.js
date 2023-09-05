function debounce(func, delay, startCallback, endCallback) {
  let timeoutId;

  return function (...args) {
    clearTimeout(timeoutId);
    if (startCallback) {
      startCallback();
    }


    timeoutId = setTimeout(() => {
      func.apply(this, args);
      if (endCallback) {
        endCallback();
      }
    }, delay);
  };
}