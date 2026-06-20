// dbConnection.js
const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database('usuarios.db', sqlite3.OPEN_READWRITE, (err) => {
    if (err) {
        console.error('Error al conectar a la base de datos:', err.message);
    } else {
        console.log('Conexión a SQLite establecida.');
    }
});

module.exports = db;
