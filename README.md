# 🎬 Movie Recommendation System with Streamlit and SQLite

This project implements a **movie recommendation web app** using **Streamlit** for the interface, **SQLite** for persistent storage, and **Pandas** for CSV handling.

---

## 🔧 Features and Functionality

### 📁 Database Management
- **Tables**:
  - `usuarios`: stores user credentials.
  - `filmes`: stores movie titles and genres.
  - `historico`: stores user history and ratings.
- **Movie Loading**: Loads movie titles and genres from a `movies (1).csv` file into the `filmes` table.

### 👤 User Management
- **Sign Up**: Users register with a unique username, email, and password.
- **Login**: Authenticates users using stored credentials.
- **Session State**: Maintains user sessions across pages using `st.session_state`.

### 🧾 Movie History
- Users can:
  - Add a movie they watched and rate it (1 to 5).
  - View their complete history with ratings.

### 🤖 Movie Recommendations
- Users receive **random movie recommendations** from the database **excluding** the ones they’ve already watched.

---

## 🖥️ Streamlit Pages (Sidebar Navigation)
- **Autenticação**: User login page.
- **Cadastro**: User registration form.
- **Perfil**: Displays logged-in user details.
- **Histórico de Filmes**: Add/view watched movies and their ratings.
- **Recomendação**: Personalized movie recommendations.
- **Logout**: Clears session and logs user out.

---

## 📦 Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Database**: SQLite (`sqlite3`)
- **Data Handling**: Pandas
- **Randomization**: Python's `random.sample`

---

## ⚠️ Notes
- Ensure `movies (1).csv` exists in the same directory with `title` and `genres` columns.
- The system is **basic** and intended as a **demo for educational use**, not production.
