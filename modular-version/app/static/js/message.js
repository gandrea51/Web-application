document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.answer-button');
    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const section = button.closest('.item');
            section.classList.toggle('open');
        });
    });
});