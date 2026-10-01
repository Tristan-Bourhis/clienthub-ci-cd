import os

import pymysql
from flask import Flask, jsonify

app = Flask(__name__)


def connect_db():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "clienthub"),
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "clienthub"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=5,
        write_timeout=5,
        autocommit=True,
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/who")
def who():
    return app.response_class("Tristan Bourhis", mimetype="text/plain")


@app.get("/clients")
def clients():
    try:
        with connect_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS clients ("
                    "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL)"
                )
                cursor.execute("SELECT id, name FROM clients ORDER BY id")
                return jsonify(cursor.fetchall())
    except pymysql.MySQLError:
        app.logger.exception("Impossible de lire les clients dans MySQL")
        return jsonify(error="Base de données indisponible"), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
