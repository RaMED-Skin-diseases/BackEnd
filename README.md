# 🧠 SkinWise – Backend

This is the backend of the **SkinWise** project — an AI-powered platform for skin disease detection. It handles user management, image uploads, AI integration, and community features where verified doctors can respond to patient posts.

## 🌐 Project Overview

The backend provides RESTful APIs to support:

- 📷 Image upload for skin disease prediction
- 🤖 AI model integration (TensorFlow via FastAPI or Django view)
- 👤 Patient and doctor registration with email/OTP verification
- 🩺 Doctor verification with ID photo upload
- 💬 Community forum (patients post, doctors reply)
- 🛡️ Authentication & authorization

## ⚙️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Django + Django REST Framework | Core backend and APIs |
| FastAPI | AI model endpoint (integrated or external) |
| PostgreSQL / SQLite | Database |
| AWS S3 / Cloudinary | Image & file storage |
| SMTP / Mailgun | OTP email verification |
| AWS | Cloud hosting |
