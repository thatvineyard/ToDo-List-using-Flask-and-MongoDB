var image = document.getElementById('question-mark');
var elem = document.getElementById('show');

image.addEventListener('click', function () {
  elem.innerHTML = image.getAttribute('alt');
});