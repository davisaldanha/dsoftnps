from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
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
    #cursor.execute('''DROP TABLE IF EXISTS admins''')
    #Tabela para armazenar os dados de satisfação
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
    #Tabela para armazenar os administradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute("SELECT * FROM admins WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO admins(username, password)
            VALUES(?,?)
        ''', ("admin", "admin"))
                   
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
app.secret_key = os.getenv("SECRET_KEY")

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

#Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM admins WHERE username = ? AND password = ?
        ''', (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin'] = username
            flash("Login efetuado com sucesso", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Usuário ou senha incorretos", "danger")
    
    return render_template('login.html')

#Rota para logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('admin', None)
    flash("Logout efetuado com sucesso", "success")
    return redirect(url_for('login'))

#Rota para dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'admin' not in session:
        flash("Faça login para acessar o dashboard", "danger")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/nps-data')
def nps_data():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute('''
        SELECT p1 FROM satisfaction WHERE p1 IS NOT NULL
    ''')
    data = cursor.fetchall()
    con.close()

    if not data:
        return {'nps':0, 'detractors': 0, 'passives': 0, 'promoters': 0}
    
    #Classificação conforme NPS
    detractors = sum(1 for x in data if x[0] <= 6)
    passives = sum(1 for x in data if 7 <= x[0] <= 8)
    promoters = sum(1 for x in data if x[0] >= 10)

    total_answers = len(data)
    perc_det = (detractors / total_answers) * 100
    perc_pas = (passives / total_answers) * 100
    perc_pro = (promoters / total_answers) * 100
    nps = perc_pro - perc_det

    return {
        'nps': nps,
        'detractors': detractors,
        'passives': passives,
        'promoters': promoters
    }

@app.route('/radar-data')
def radar_data():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    cursor.execute('''
        SELECT AVG(p1), AVG(p2), AVG(p3), AVG(p4), AVG(p5), AVG(p6), AVG(p7), AVG(p8), AVG(p9), AVG(p10)
        FROM satisfaction
    ''')

    data = cursor.fetchone()
    con.close()

    questions = [
       "Recomendação", "Qualidade", "Atendimento", "Rapidez", "Preço", "Variedade", "Ambiente", "Busca", "Pagamento", "Custo-benefício"
    ]

    return jsonify({"labels": questions, "values": [round(m, 1) if m else 0 for m in data]}) 

@app.route('/bars-data')
def bars_data():
    con = sqlite3.connect('database.db')
    cursor = con.cursor() 

    data = {}

    for i in range(1, 11):
        cursor.execute(f"""
            SELECT p{i}, COUNT(*) FROM satisfaction GROUP BY p{i} ORDER BY p{i}
        """)
        results = cursor.fetchall()
        data[f'p{i}'] = {nota: total for nota, total in results}
    
    con.close()
    return jsonify(data)

if __name__ == '__main__':
    configure_database()
    send_email()
    app.run(debug=True)

