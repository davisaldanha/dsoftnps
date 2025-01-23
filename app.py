from flask import Flask, request, render_template, redirect, url_for
import smtplib
import schedule
import sqlite3

#Excluir banco de dados
def drop_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE satisfaction')
    conn.commit()
    conn.close()

#Configuração do banco de dados
def configure_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS satisfaction(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
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
        return redirect(url_for('already_submitted'))
    finally: 
        conn.close()

app = Flask(__name__)

#Rota para a página de satisfação do cliente
@app.route('/satisfacao', methods=['GET', 'POST'])
def satisfaction():
    questions = [
        "Qual a probabilidade de você recomendar nossa loja para um amigo ou colega?",
        "Como você avalia a qualidade dos nossos produtos?",
        "Como você avalia o atendimento que recebeu?",
        "A rapidez no atendimento atendeu suas expectativas?",
        "O preço dos produtos é justo?",
        "A variedade de produtos foi satisfatória?",
        "O ambiente da loja é agradável?",
        "Você encontrou tudo o que procurava?",
        "Como você avalia a facilidade de pagamento?",
        "Considera que nossos serviços têm boa relação custo-benefício?"
    ]

    if request.method == 'POST':
        email = request.form.get("email")
        phone = request.form.get("phone")
        answers_list = [
            int(request.form.get(f"p{i}")) for i in range(1, 11)
        ]
        if email and phone and all(answers_list):
           add_answers(email, phone, answers_list)
           return redirect(url_for('already_submitted'))
    return render_template('satisfaction.html', questions=questions, enumerate=enumerate)

#Rota para a página de agradecimento
@app.route('/obrigado', methods=['GET'])
def already_submitted():
    return render_template('already_submitted.html')

if __name__ == '__main__':
    drop_database()
    configure_database()
    app.run(debug=True)

