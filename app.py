from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, schedule
import sqlite3, logging, time, os

load_dotenv()

logging.basicConfig(filename="lgpd_logs.log", level=logging.INFO)

#Função para registrar logging
def log_info(message, email, phone):
    logging.info(f"{message} - Email: {email} - Phone: {phone} - Data: {time.strftime('%Y-%m-%d %H:%M:%S')}")


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
            p6 INTEGER, p7 INTEGER, p8 INTEGER, p9 INTEGER, p10 INTEGER,
            created_at DATE DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

#Função para adicionar respostas ao banco de dados
def add_answers(email, phone, answers):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO satisfaction(email, phone, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (email, phone, *answers))
        conn.commit()
        log_info("Dados cadastrados com sucesso", email, phone)
    except sqlite3.IntegrityError:
        return redirect(url_for('already_submitted'))
    finally: 
        conn.close()

#Função para limpar dados antigos do banco de dados
#Agendar com schedule para rodar anualmente
def clear_old_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM emails WHERE DATE(created_at) < DATE('now', '-1 year')
    ''')
    conn.commit()
    conn.close()

#Função para obter os emails
def get_emails():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT email FROM satisfaction
    ''')
    emails = cursor.fetchall()
    conn.close()
    return emails

#Função para enviar email
def send_email():
    emails = get_emails()

    if emails:
        try:
            with smtplib.SMTP(os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT")) as server:
                server.starttls()
                server.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
                    
            for email_tuple in emails:
                try:
                    email = email_tuple[0]
                    message = MIMEMultipart()
                    message['From'] = os.getenv("EMAIL")
                    message['TO'] = email
                    message['Subject'] = 'Ofertas da Semana - Loja X'

                    content = "<h1>Confira nossas ofertas da semana!</h1><p>Visite nossa loja para aproveitar.</p>"
                    message.attach(MIMEText(content, 'html'))

                
                    server.sendmail(os.getenv("EMAIL"), email, message.as_string())
                    log_info("Email enviado com sucesso", email, "N/A")
                except Exception as e:
                    log_info(f"Erro ao enviar emails: {e}", "N/A", "N/A")

        except Exception as e:
            log_info(f"Erro ao conectar ao servidor: {e}", "N/A", "N/A")
            

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

#Rota para politica de privacidade
@app.route('/politica-de-privacidade', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')

if __name__ == '__main__':
    configure_database()
    send_email()
    app.run(debug=True)

