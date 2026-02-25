document.addEventListener('click', function (e) {
  const btn = e.target.closest('.password-toggle');
  if (!btn) return;
  // find input in same parent
  const wrapper = btn.closest('.input-with-toggle');
  if (!wrapper) return;
  const input = wrapper.querySelector('input');
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '🙈';
    btn.setAttribute('aria-label', 'Hide password');
  } else {
    input.type = 'password';
    btn.textContent = '👁️';
    btn.setAttribute('aria-label', 'Show password');
  }
});

function updateFilledState(input) {
  if (!input) return;
  if (input.value && input.value.length > 0) input.classList.add('filled');
  else input.classList.remove('filled');
}

document.addEventListener('input', function (e) {
  const target = e.target;
  if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
    updateFilledState(target);
  }
});

// initialize on DOM ready
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('input, textarea').forEach(function (el) {
    updateFilledState(el);
  });
  console.log('auth.js loaded and initialized');
});
