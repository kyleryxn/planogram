document.getElementById('file').addEventListener('change', function () {
    const display = document.querySelector('.file-chosen');
    display.textContent = this.files.length ? this.files[0].name : 'No file chosen';
});

document.querySelector('.upload-form').addEventListener('submit', function () {
    const btn = document.getElementById('upload-btn');
    const loading = document.getElementById('loading-state');
    btn.disabled = true;
    btn.style.display = 'none';
    loading.classList.add('visible');
});
