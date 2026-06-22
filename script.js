document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            // Logic for items.html (Grid view)
            const itemsContainer = document.getElementById('items-container');
            if (itemsContainer) {
                data.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <img src="${item.image}" alt="${item.name}">
                        <h3>${item.name}</h3>
                        <p class="price">$${item.price.toFixed(2)}</p>
                        <a href="item.html?id=${item.id}" class="btn" style="margin-top:10px;">View Details</a>
                    `;
                    itemsContainer.appendChild(card);
                });
            }

            // Logic for item.html (Single item view)
            const itemDetailContainer = document.getElementById('item-detail-container');
            if (itemDetailContainer) {
                const urlParams = new URLSearchParams(window.location.search);
                const itemId = urlParams.get('id');
                const item = data.find(i => i.id === itemId);

                if (item) {
                    document.getElementById('item-image').src = item.image;
                    document.getElementById('item-name').textContent = item.name;
                    document.getElementById('item-price').textContent = `$${item.price.toFixed(2)}`;
                    document.getElementById('item-desc').textContent = item.description;
                    document.getElementById('item-buy-btn').href = item.stripe_link;
                } else {
                    itemDetailContainer.innerHTML = '<h2>Item not found</h2><a href="items.html">Go back to items</a>';
                }
            }
        })
        .catch(error => console.error('Error loading inventory:', error));
});