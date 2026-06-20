from flask import Flask, request, render_template
import os
import json
import requests
import sqlite3

def insert_book(db, book_title, book_authors):
    try:
        # Ejecuta la consulta INSERT
        db.execute(
            "INSERT INTO UserLibrary (title, author) VALUES (?, ?)",
            (book_title, book_authors)
        )
        db.commit()  # Confirma la transacción
        print(f"Libro '{book_title}' agregado correctamente.")
    except sqlite3.Error as e:
        print(f"Error al agregar el libro: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # Supongamos que ya tienes una conexión a la base de datos 'db'
    book_title = "El Gran Gatsby"
    book_authors = "F. Scott Fitzgerald"
    insert_book(db, book_title, book_authors)
