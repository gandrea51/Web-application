document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('.fint-write');
    const genreItems = document.querySelectorAll('.find-item');
  
    searchInput.addEventListener('input', () => {
      const query = searchInput.value.toLowerCase().trim();
  
      genreItems.forEach(item => {
        const genreName = item.querySelector('.name').textContent.toLowerCase();
        if (genreName.includes(query)) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });