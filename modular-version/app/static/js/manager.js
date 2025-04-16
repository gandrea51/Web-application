document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector(".find-search input[type='text']");
    const bookItems = document.querySelectorAll(".dynamo-item");

    searchInput.addEventListener("input", function () {
        const query = this.value.toLowerCase();

        bookItems.forEach(item => {
            const title = item.querySelector(".book-title").textContent.toLowerCase();
            const author = item.querySelector(".book-author").textContent.toLowerCase();

            if (title.includes(query) || author.includes(query)) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }
        });
    });
});