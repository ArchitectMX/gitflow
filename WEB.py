from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def mission():
    return "<h1>Миссия Колонизация Марса</h1>"

@app.route('/index')
def motto():
    return "<h1>И на Марсе будут яблони цвести!</h1>"

@app.route('/promotion')
def promotion():
    text = "Человечество вырастает из детства.<br>"
    text += "Человечеству мала одна планета.<br>"
    text += "Мы сделаем обитаемыми безжизненные пока планеты.<br>"
    text += "И начнем с Марса!<br>"
    text += "Присоединяйся!"
    return f"<h1>{text}</h1>"

@app.route('/image_mars')
def image_mars():
    return '''
    <html>
        <head>
            <title>Привет, Марс!</title>
        </head>
        <body>
            <img src="/static/image_mars.png" alt="Марс" width="500">
        </body>
    </html>
    '''
#             <h1>Жди нас, Марс!</h1>
#             <p>Красная планета ждет нас!</p>

@app.route('/promotion_image')
def promotion_image():
    return '''
    <html>
        <head>
            <title>Привет, Марс!</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body class="text-center">
            <div class="container">
                <h1 class="text-danger">Жди нас, Марс!</h1>
                <img src="/static/img/image_mars.png" class="img-fluid" alt="Марс">
                <p class="mt-3">Человечество вырастает из детства.</p>
                <p>Человечеству мала одна планета.</p>
                <p>Мы сделаем обитаемыми безжизненные пока планеты.</p>
                <p>И начнем с Марса!</p>
                <p class="fw-bold">Присоединяйся!</p>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
