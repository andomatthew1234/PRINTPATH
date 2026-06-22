Planning Document: PrintPath
1. Project Overview

PrintPath is a localized 3D printing service designed for the school community. It offers a streamlined interface for students to browse and purchase pre-designed models or submit custom requests, with physical delivery facilitated at school.
2. Technical Stack

    Hosting: GitHub Pages (Static site).

    Frontend: HTML5, CSS3 (Light theme with #00AE42 accent), and Vanilla JavaScript.

    CMS: A local Python-based GUI (built with tkinter or customtkinter) that manages a data.json file. This file acts as the single source of truth for the inventory.

    Payments: Stripe Checkout (Buy Links).

    Form Handling: Formspree or similar static-form service to collect customer details (Name, Email, Address, Phone, File/Link).

3. Site Architecture & Pages

    index.html: The landing page. Highlights the value proposition, links to the product catalog, and explains the "How it Works" process (Order -> Print -> Deliver).

    items.html: A responsive grid displaying available preset models. Data is fetched dynamically from the data.json file.

    item.html: A template page that populates based on the selection from items.html. Includes model details and the Stripe Buy Link.

    custom.html (Proposed): A form-based page for custom prints.

        Fields: Name, Email, Address, Phone, File Upload/Link.

        Payment: A "Pay Deposit" Stripe link or a manual follow-up system.

    status.html (Future): Placeholder page for tracking order progression (To be implemented).

4. Workflow & CMS Logic

    Admin Workflow:

        You run a local Python script (admin_cms.py) on your PC.

        The script provides a GUI to add/edit/delete models.

        Saving updates the local data.json.

        You commit/push the updated data.json to your GitHub repository to update the live site.

    Customer Workflow:

        Presets: Select item -> View details -> Click "Buy" -> Redirect to Stripe -> Order received.

        Custom: Fill form -> Upload file/Link -> Submit -> You receive order details -> Process manually.

5. Data Requirements (for data.json)
JSON

[
  {
    "id": "green-goblin",
    "name": "Green Goblin",
    "price": 15.00,
    "image": "path/to/img.jpg",
    "stripe_link": "https://buy.stripe.com/..."
  }
]

6. Development Checklist

    [ ] CMS GUI: Develop admin_cms.py using tkinter to read/write data.json.

    [ ] Frontend Shell: Create core HTML/CSS templates using the #00AE42 color scheme.

    [ ] Data Integration: Write JavaScript in items.html to fetch and render the JSON inventory.

    [ ] Form Setup: Configure form handling for custom orders (using a tool like Formspree to email you the student details/uploads).

    [ ] Deployment: Configure GitHub Pages to host the static files.