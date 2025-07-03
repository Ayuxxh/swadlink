# 🧾 SwadLink

**SwadLink** is a lightweight, QR-powered digital menu and order management system designed for cafés and restaurants in India. It simplifies daily operations with features like real-time KOT, table tracking, WhatsApp billing, and a mobile-friendly owner dashboard.

---

## 🚀 Features

- 📱 **QR-Based Digital Menu** – Let customers scan and order easily.
- 🍽️ **KOT System** – Real-time kitchen order ticket updates.
- 🧾 **WhatsApp Billing** – Share bills instantly with customers.
- 🪑 **Table Management** – Track tables and current orders live.
- 📊 **Owner Dashboard** – View sales stats, top items, and feedback.
- 💬 **Customer Feedback System** – Collect and analyze feedback.

---

## 🛠 Tech Stack

- **Backend**: Django  
- **Frontend**: Tailwind CSS, HTML  
- **Database**: PostgreSQL  
- **Optional**: Redis + Celery (for advanced task handling)

---

## 🧑‍💻 Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/swadlink.git
   cd swadlink
   ```

2. **Set up a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**  
   Create a `.env` file and set your database config and secret keys.

5. **Run migrations**  
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**  
   ```bash
   python manage.py runserver
   ```

---

## 📌 Project Goals

SwadLink aims to be a simple, customizable alternative to platforms like Petpooja — made for local cafés and restaurants that want better control and lower costs.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🙌 Contributing

Have ideas or improvements? Feel free to fork, raise issues, or submit pull requests!

---

## 📬 Contact

**Developer:** Ayush Jadhav  
**Email:** your.email@example.com  
**Instagram:** [@swadlink](https://instagram.com/swadlink)
