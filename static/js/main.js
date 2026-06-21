function changeQty(delta) {
  const input = document.getElementById('qty');
  if (!input) return;
  const val = parseInt(input.value) + delta;
  const min = parseInt(input.min) || 1;
  const max = parseInt(input.max) || 99;
  input.value = Math.max(min, Math.min(max, val));
}

function changeQtyForm(btn, delta) {
  const input = btn.parentElement.querySelector('input[type=number]');
  if (!input) return;
  const val = parseInt(input.value) + delta;
  input.value = Math.max(0, Math.min(99, val));
}
