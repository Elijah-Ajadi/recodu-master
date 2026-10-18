# Recodu: Smart Health Monitoring & Patient Management

Recodu is a modern, high-performance web application built with Django, designed for medical clinics and volunteer organizations to streamline patient intake and track clinical vitals with precision.

## 🚀 Key Features

- **Efficient Patient Intake**: Register new patients in under 15 seconds with a streamlined, mobile-first interface.
- **Smart Vitals Tracking**: Record and monitor Blood Pressure (BP), Pulse, Temperature, and Glucose levels with real-time clinical threshold validation.
- **Data Visualization**: Interactive medical history timelines and trends powered by Chart.js.
- **Role-Based Access Control (RBAC)**: Secure access levels for Unit Heads and Volunteers to ensure data integrity and privacy.
- **Clinical Validation Engine**: Real-time feedback on vitals (Normal, Elevated, Critical) based on medical standards.
- **Reporting & Export**: Generate comprehensive CSV reports for data analysis and clinical review.

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7 (Python 3.12+)
- **Database**: PostgreSQL (Neon for production), SQLite (for local development)
- **Deployment**: Vercel (Edge-ready)
- **Frontend**: Vanilla CSS & JavaScript (Modern ES6+), Chart.js
- **Assets**: WhiteNoise for efficient static file serving

## ⚙️ Local Setup

### Prerequisites
- Python 3.12 or higher
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/recodu.git
   cd recodu
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables:**
   Create a `.env` file in the root directory and add:
   ```env
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   # For local SQLite, you can omit DATABASE_URL or set it to a local postgres if preferred
   ```

5. **Run Migrations & Start Server:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000` to see the application.

## ☁️ Deployment

Recodu is optimized for deployment on **Vercel** with **Neon PostgreSQL**.

1. Connect your GitHub repository to Vercel.
2. Set the environment variables in the Vercel dashboard (`DJANGO_SECRET_KEY`, `DATABASE_URL`, etc.).
3. Vercel will automatically run `build.sh` and deploy your application.

See [DEPLOYMENT.md](DEPLOYMENT.md) for a more detailed guide.

## 📝 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

Built with ❤️ for better healthcare.
