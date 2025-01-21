from Flask import Flask, request, render_template, redirect, url_for
import smtplib
import schedule
import sqlite3

#Configuração do banco de dados
def configure_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS satisfaction(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            p1 INTEGER, p2 INTEGER, p3 INTEGER, p4 INTEGER, p5 INTEGER,
            p6 INTEGER, p7 INTEGER, p8 INTEGER, p9 INTEGER, p10 INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_answers(email, answers):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO satisfaction(email, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
        ''', (email, *answers))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"O Email {email} já enviou repostas.")
    finally:
        conn.close()

app = Flask(__name__)

#Rota para a página de satisfação do cliente
@app.route('/satisfacao', methods=['GET', 'POST'])
def satisfaction():
    if request.method == 'POST':
        email = request.form.get("email")
        answers = [
            int(request.form.get(f"p{i}")) for i in range(1, 11)
        ]
        if email and all(answers):
           add_answers(email, answers)
           return redirect(url_for('satisfacao'))
    return render_template('satisfaction.html')



if __name__ == '__main__':
    configure_database()
    app.run(debug=True)

