from flask import Flask, render_template_string, request

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

@app.route('/astronaut_selection', methods=['GET', 'POST'])
def astronaut_selection():
    if request.method == 'POST':
        return "<h1>Форма отправлена!</h1>"
    return '''
    <html>
        <head>
            <title>Отбор астронавтов</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">Анкета претендента</h1>
                <h3 class="text-center">на участие в миссии</h3>
                <form method="post" class="p-4 bg-light border rounded">
                    <input type="text" class="form-control mb-2" placeholder="Введите фамилию" required>
                    <input type="text" class="form-control mb-2" placeholder="Введите имя" required>
                    <input type="email" class="form-control mb-2" placeholder="Введите адрес почты" required>
                    <select class="form-control mb-2">
                        <option>Начальное</option>
                        <option>Среднее</option>
                        <option>Высшее</option>
                    </select>
                    <label>Какие у Вас есть профессии?</label><br>
                    <input type="checkbox"> Инженер-исследователь<br>
                    <input type="checkbox"> Инженер-строитель<br>
                    <input type="checkbox"> Пилот<br>
                    <input type="checkbox"> Экзобиолог<br>
                    <input type="checkbox"> Врач<br>
                    <input type="checkbox"> Инженер по терраформированию<br>
                    <label class="mt-2">Укажите пол</label><br>
                    <input type="radio" name="gender" required> Мужской
                    <input type="radio" name="gender"> Женский<br>
                    <textarea class="form-control mt-2" placeholder="Почему Вы хотите принять участие в миссии?"></textarea>
                    <label class="mt-2">Приложите фотографию</label>
                    <input type="file" class="form-control mb-2">
                    <input type="checkbox"> Готовы остаться на Марсе?<br>
                    <button type="submit" class="btn btn-primary mt-2">Отправить</button>
                </form>
            </div>
        </body>
    </html>
    '''


@app.route('/choice/<planet_name>')
def choice(planet_name):
    html_content = '''
    <html>
        <head>
            <title>Выбор планеты для освоения</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">Миссия Колонизации</h1>
                <h2 class="text-center text-success">Выбор планеты: {{ planet_name }}</h2>
                <div class="card">
                    <div class="card-body">
                        <h3 class="card-title">Предлагаем начать освоение планеты <strong>{{ planet_name }}</strong></h3>
                        <p class="card-text">Наша миссия направлена на освоение новых миров, и <strong>{{ planet_name }}</strong> — это наш следующий шаг. В ближайшие годы мы планируем начать подготовку для создания на этой планете первой человеческой колонии.</p>
                        <p>Какие этапы предстоят нам?</p>
                        <ul>
                            <li>Этап 1: Изучение атмосферы и условий на планете.</li>
                            <li>Этап 2: Создание обитаемых станций и терраформирование.</li>
                            <li>Этап 3: Размещение первой группы исследователей и астронавтов.</li>
                        </ul>
                        <p class="mt-3">Присоединяйтесь к нашей миссии и помогите освоить {{ planet_name }}!</p>
                        <p class="text-muted">Будущее человечества начинается с колонизации планет!</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''

    return render_template_string(html_content, planet_name=planet_name)


@app.route('/results/<nickname>/<int:level>/<float:rating>')
def results(nickname, level, rating):
    if level < 1 or level > 5:
        return "<h1>Ошибка! Уровень должен быть от 1 до 5.</h1>", 400
    if rating < 0.0 or rating > 10.0:
        return "<h1>Ошибка! Рейтинг должен быть от 0.0 до 10.0.</h1>", 400

    if rating >= 8.0:
        result_message = "Поздравляем! Вы прошли этот этап с отличием!"
        result_class = "text-success"
    elif rating >= 5.0:
        result_message = "Хороший результат! Продолжайте в том же духе!"
        result_class = "text-warning"
    else:
        result_message = "Не расстраивайтесь, вам нужно улучшить результаты для следующего этапа."
        result_class = "text-danger"

    html_content = '''
    <html>
        <head>
            <title>Результаты отбора</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">Результаты отбора на миссию</h1>
                <div class="card">
                    <div class="card-body">
                        <h2 class="card-title">Претендент: {{ nickname }}</h2>
                        <h3 class="text-success">Этап отбора: {{ level }}</h3>
                        <p class="card-text">Рейтинг претендента: <strong>{{ rating }}</strong></p>
                        <h4 class="{{ result_class }}">{{ result_message }}</h4>
                        <p class="mt-3">Похоже, вы прошли этот этап успешно!</p>
                        <p class="text-muted">Следующий шаг — готовность к подготовке на следующую планету!</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    '''

    return render_template_string(html_content, nickname=nickname, level=level, rating=rating,
                                  result_message=result_message, result_class=result_class)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
