// ============================================================================
// BO1 Zombies — Modo Online: configuração do Firebase (fornecida pelo usuário)
// https://firebase.google.com/docs/web/setup#available-libraries
// ============================================================================

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBAR6HwrGBmwUxVDvIVuGYar82Lozg1Sck",
  authDomain: "kaka-ca0ff.firebaseapp.com",
  databaseURL: "https://kaka-ca0ff-default-rtdb.firebaseio.com",
  projectId: "kaka-ca0ff",
  storageBucket: "kaka-ca0ff.firebasestorage.app",
  messagingSenderId: "803477967370",
  appId: "1:803477967370:web:fc8b9614f3e319c8c205f3"
};

// Initialize Firebase
const app = firebase.initializeApp(firebaseConfig);

// Exposto para o app.js
window.BO1Z_APP = app;
window.BO1Z_FIREBASE_CONFIG = firebaseConfig;
