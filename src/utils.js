/* eslint-disable */

function binaryIndexOf(searchElement) {
  let minIndex = 0;
  let maxIndex = this.length - 1;
  let currentIndex;
  let currentElement;

  while (minIndex <= maxIndex) {
    currentIndex = (minIndex + maxIndex) / 2 | 0;
    currentElement = this[currentIndex];

    if (currentElement < searchElement) {
      minIndex = currentIndex + 1;
    }
    else if (currentElement > searchElement) {
      maxIndex = currentIndex - 1;
    }
    else {
      return currentIndex;
    }
  }
  return [maxIndex, minIndex];
}

// Re-maps a number from one range to another.
function map(x, in_min, in_max, out_min, out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

export default { binaryIndexOf, map };
