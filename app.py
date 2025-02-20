from flask import Flask, render_template, request
from obliczenia.geometria import rysuj

app = Flask(__name__)

@app.route('/')
def index():
    """
    Strona główna z formularzem do wprowadzania współrzędnych.
    """
    return render_template('formularz.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """
    Odbiera współrzędne odcinków z formularza,
    wywołuje funkcję rysującą oraz zwraca stronę z wynikiem.
    """
    # Pobranie danych z formularza
    x1 = float(request.form.get('x1'))
    y1 = float(request.form.get('y1'))
    x2 = float(request.form.get('x2'))
    y2 = float(request.form.get('y2'))

    x3 = float(request.form.get('x3'))
    y3 = float(request.form.get('y3'))
    x4 = float(request.form.get('x4'))
    y4 = float(request.form.get('y4'))

    odcinek1 = (x1, y1, x2, y2)
    odcinek2 = (x3, y3, x4, y4)

    # Wygenerowanie wykresu i pobranie opisu przecięcia
    wykres_base64 = rysuj(odcinek1, odcinek2)

    # Render szablonu wynikowego
    return render_template(
        'wyniki.html',
        wykres_base64=wykres_base64
    )


if __name__ == '__main__':
    app.run(debug=True)
