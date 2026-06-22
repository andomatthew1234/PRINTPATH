document.addEventListener('DOMContentLoaded', () => {
    // --- PART 1: INVENTORY LOGIC ---
    // Added a check to prevent inventory fetch errors from breaking the tracker
    fetch('data.json')
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
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
        .catch(error => console.warn('Inventory not loaded on this page or data.json is missing:', error));

    // --- PART 2: ORDER TRACKING LOGIC ---
    const statusForm = document.getElementById('status-form');
    if (statusForm) {
        statusForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Intercept form submission
            const orderId = document.getElementById('order_id_input').value.trim().toUpperCase();
            const errorDiv = document.getElementById('status-error');
            const resultDiv = document.getElementById('status-result');
            const searchDiv = document.getElementById('status-search');

            fetch('prints.json')
                .then(res => {
                    if (!res.ok) throw new Error("Network response was not ok");
                    return res.json();
                })
                .then(data => {
                    const order = data.find(o => o.order_id === orderId);
                    if (order) {
                        errorDiv.style.display = 'none';
                        searchDiv.style.display = 'none';
                        resultDiv.style.display = 'block';

                        let title = '';
                        let desc = '';

                        switch(order.status) {
                            case 'PENDING':
                                title = "We're processing your order";
                                desc = "We need some time to double check everything and process your order.";
                                break;
                            case 'QUEUE':
                                title = "Your print is waiting in the print queue.";
                                desc = "We've received your order - yay! When your print is ready to be printed, we'll print it.";
                                break;
                            case 'PRINTING':
                                title = "We're printing your print.";
                                desc = "Get ready to own the print - we're printing your order! Check back here soon.";
                                break;
                            case 'WAITING':
                                title = "We're waiting to attempt delivery.";
                                desc = "If nothing happens, email me at 'matthew@andomail.com'.";
                                break;
                            case 'DELIVERED':
                                title = "The print has been delivered!";
                                desc = "Yay, the print was successfully received by you. Thanks!";
                                break;
                            default:
                                title = "Status Unknown";
                                desc = "We are reviewing your order. Please check back later.";
                        }

                        document.getElementById('status-title').textContent = title;
                        document.getElementById('status-desc').textContent = desc;
                        document.getElementById('display-order-id').textContent = order.order_id;
                        document.getElementById('display-name').textContent = order.name;
                        document.getElementById('display-item').textContent = order.item_name;
                    } else {
                        errorDiv.style.display = 'block';
                        errorDiv.textContent = 'Order ID not found. Please check your ID and try again.';
                    }
                })
                .catch(err => {
                    console.error('Error fetching orders:', err);
                    errorDiv.style.display = 'block';
                    errorDiv.textContent = 'System error: Could not connect to the database. Please try again later.';
                });
        });
    }
});