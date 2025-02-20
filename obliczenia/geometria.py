import io
import base64
import matplotlib.pyplot as plt
import math
from decimal import Decimal

# współczynniki m i b dla prostej, na której położony jest odcinek
def wspolczynniki(odcinek):
    x1, y1, x2, y2 = odcinek
    # Sprawdzamy, czy odcinek nie jest pionowy, bo jeśli tak, nie ma współczynnika kierunkowego m, a b jest równe x1 i x2:
    if x1 == x2:
        m = None
        b = x1
    # W przeciwnym razie możemy określić m i b:
    else:
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
    return m, b

# współrzędne początku i końca zakresu nachodzenia się odcinków lub None, jeśli odcinki się nie nachodzą
def nachodzace(odcinek1, odcinek2):
    # współrzędne obu końców każdego odcinka
    x1, y1, x2, y2 = odcinek1
    x3, y3, x4, y4 = odcinek2

    # sortowanie punktów w kierunku osi X i Y
    x1, x2 = min(x1, x2), max(x1, x2)
    x3, x4 = min(x3, x4), max(x3, x4)
    y1, y2 = min(y1, y2), max(y1, y2)
    y3, y4 = min(y3, y4), max(y3, y4)

    # punkty końcowe rzutów odcinków na obie osie
    x_od, x_do = max(x1, x3), min(x2, x4)
    y_od, y_do = max(y1, y3), min(y2, y4)

    # Sprawdzamy, czy rzuty nachodzą na siebie.
    if x_od <= x_do and y_od <= y_do:
        # Jeśli tak, ustalamy kolejność współrzędnych y.
        # Jeśli współrzędna y początku pierwszego odcinka (y1) jest większa niż współrzędna y końca zakresu
        # nachodzenia (y_do), zamieniamy końce nachodzenia miejscami.
        if y1 > y_do:
            y_od, y_do = y_do, y_od    

        # Zwracamy współrzędne początku i końca zakresów nachodzenia.
        return (x_od, y_od, x_do, y_do)
    # Jeśli nie nachodzą, zwracamy None.
    return None

# zaokrąglanie dynamiczne (tyle, ile trzeba, np. aby np. nie zaokrąglił 0.0000015 do 0.000)
def zd(liczba):
    # Jeśli wartość bezwzględna liczby jest większa niż 0.01,
    # zaokrąglamy liczbę do 3 miejsc po przecinku.
    if abs(liczba) > 0.01:
        liczba = round(liczba, 3)
        
    # usuwamy zbędne zera
    liczba = Decimal(str(liczba)).normalize()  
    
    return str(liczba) if 'E' not in str(liczba) else f"{liczba:.10f}".rstrip('0')

# zwraca przybliżony zakres uwzględniając niedoskonałości z arytmetyki zmiennoprzecinkowej
def przyblizony_zakres(x, x1, x2, tolerancja=1e-9):
    return (x1 - tolerancja) <= x <= (x2 + tolerancja)

def przeciecie(odcinek1, odcinek2):
    '''
    Funkcja zwracająca informację na temat przecinania się odcinków, a także ewentualnie punkt
    przecięcia lub zakres nachodzenia na siebie odcinków.
    Każdy odcinek to 4-krotka ze współrzędnymi obu końców odcinka.
    '''
    # punkty końcowe odcinka 1
    x1, y1, x2, y2 = odcinek1

    # punkty końcowe odcinka 2
    x3, y3, x4, y4 = odcinek2

    # sortowanie punktów w kierunku osi X i Y
    x1, x2 = min(x1, x2), max(x1, x2)
    x3, x4 = min(x3, x4), max(x3, x4)
    y1, y2 = min(y1, y2), max(y1, y2)
    y3, y4 = min(y3, y4), max(y3, y4)

    # Aby sprawdzić, czy odcinki się przecinają, należy sprawdzić, czy współliniowe do nich proste
    # się przecinają. Jeśli tak, należy sprawdzić, czy przecinają się w jednym punkcie, czy częściowo
    # na siebie nachodzą:

    ### Wyznaczamy proste, na których leżą odcinki oraz ich współczynniki kierunkowe i wyrazy wolne. ###

    #     Wyznaczenie prostej polega na wyznaczeniu jej rownania. Dla prostej przechodzącej przez 2 punkty
    #     o współrzędnych (x1, y1) i (x2, y2) równanie można wyznaczyć w postaci kierunkowej y = mx + b, gdzie:
    #     m - współczynnik kierunkowy, m = (y2 - y1) / (x2 - x1),
    #     b - wyraz wolny, który możemy wyznaczyć przez podstawienie współrzędnych jednego punktu do równania

    # Nas interesują współczynniki m i b dla obu prostych:

    # prosta, na której leży odcinek 1
    m1, b1 = wspolczynniki(odcinek1)

    # prosta, na której leży odcinek 2
    m2, b2 = wspolczynniki(odcinek2)

    ### Sprawdzamy równoległość prostych. ###

    # Proste są równoległe, kiedy mają takie same współczynniki kierunkowe. Jeśli proste są równoległe, to:
    #     - są rozłączne, m1 == m2, b1 != b2
    #       lub
    #     - są współliniowe, m1 == m2, b1 == b2 - leżące na nich odcinki mogą być rozłączne lub na siebie nachodzić
    # m1 == m2 mogłoby zwrócić błędny wynik dla bardzo małych wartości, więc sprawdzamy, czy są bliskie.     
    if (m1 is None and m2 is None) or ((m1 is not None and m2 is not None) and math.isclose(m1, m2, rel_tol=1e-9)):
        # proste rozłączne #
        if b1 != b2:
            return None
        # proste współliniowe #
        # Sprawdzamy, czy odcniki na siebie nachodzą i w jakim zakresie.
        # Jeśli tak, zwracamy współrzędne początku i końca zakresu nachodzenia.
        # Jeśli nie, to znaczy, że odcinki leżą na jednej prostej, ale nie nachodzą się i funkcja zwróci None.
        return nachodzace(odcinek1, odcinek2)

    ### Sprawdzamy, w którym punkcie proste się przecinają. ###

    # Jeżeli proste nie są równoległe, to na pewno się przecinają. Musimy sprawdzić, czy ten punkt
    # przecięcia należy do obu odcinków.

    # Określamy punkt przecięcia prostych.
    # Najpierw sprawdzamy przypadek, w którym żadna z prostych nie jest pionowa:
    if m1 is not None and m2 is not None:
        # Punkt przecięcia to punkt wspólny prostych. Jego współrzędne to (x, y).
        # Możemy zapisać równania obu prostych:
        # y = m1 * x + b1
        # y = m2 * x + b2
        # czyli m1 * x + b1 = m2 * x + b2,
        # czyli m1 * x - m2 * x = b2 - b1,
        # czyli (m1 - m2) * x = b2 - b1,
        # czyli x = (b2 - b1) / (m1 - m2)
        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1
    # Jeśli m1 lub m2 jest None, to mamy prostą pionową. Wtedy współrzędną y musimy obliczyć
    # używając równania prostej niepionowej.

    # Sprawdzamy 2 przypadki:
    # 1) pierwsza prosta jest pionowa
    elif m1 is None:
        x = b1
        y = m2 * x + b2
    # 2) druga prosta jest pionowa
    elif m2 is None:
        x = b2
        y = m1 * x + b1

    ### Sprawdzamy, czy odcinki się przecinają. ###

    # Odcinki przecinają się tylko wtedy, kiedy punkt przecięcia prostych (x, y) należy do obu odcinków.
    # Odcinki są już posortowane od lewej do prawej i od dołu do góry.        
    if (przyblizony_zakres(x, x1, x2) 
        and przyblizony_zakres(y, y1, y2) 
        and przyblizony_zakres(x, x3, x4) 
        and przyblizony_zakres(y, y3, y4)):
        return x, y

    # Jeśli powyższy warunek nie jest spełniony, odcinki się nie przecinają
    return None


def rysuj(odcinek1, odcinek2):
    '''
    Funkcja rysuje oba odcinki w układzie współrzędnych i zaznacza ich punkt przecięcia
    albo zakresy nachodzenia się odcinków, o ile istnieją.
    '''

    # punkty końcowe odcinka 1
    x1, y1, x2, y2 = odcinek1

    # punkty końcowe odcinka 2
    x3, y3, x4, y4 = odcinek2

    # rysowanie odcinków
    plt.figure(figsize=(6, 3))
    # jeśli odcinek1 zaczyna się i kończy w tym samym punkcie
    if x1 == x2 and y1 == y2:
        plt.scatter(x1, y1, color="blue", label="Odcinek 1 (odcinek → punkt)")
    # jeśli odcinek1 zaczyna się i kończy w różnych punktach
    else:
        plt.plot([x1, x2], [y1, y2], label="Odcinek 1", color="blue", linewidth=8, alpha=.5)

    # jeśli odcinek2 zaczyna się i kończy w tym samym punkcie
    if x3 == x4 and y3 == y4:
        plt.scatter(x3, y3, color="green", label="Odcinek 2 (odcinek → punkt)")
    # jeśli odcinek1 zaczyna się i kończy w różnych punktach
    else:
        plt.plot([x3, x4], [y3, y4], label="Odcinek 2", color="green", linewidth=8, alpha=.5)


    # zaznaczenie punktu przecięcia lub obu końców zakresu nachodzenia
    wspolrzedne = przeciecie(odcinek1, odcinek2)
   
    if wspolrzedne:
        # Jeśli odcinki na siebie nachodzą, funkcja przeciecie zwróciła współrzędne obu końców zakresu
        # nachodzenia, czyli 4 liczby.
        if len(wspolrzedne) == 4:
            poczatek = wspolrzedne[:2]
            koniec = wspolrzedne[2:]
            plt.scatter(*poczatek, color="black", s=150, label=f"Początek zakresu nachodzenia ({zd(poczatek[0])}, {zd(poczatek[1])})")
            plt.scatter(*koniec, color="gray", s=150, label=f"Koniec zakresu nachodzenia ({zd(koniec[0])}, {zd(koniec[1])})")
            plt.plot([poczatek[0], koniec[0]], [poczatek[1], koniec[1]], label="Zakres nachodzenia", color="red", linestyle="--", linewidth=2)
            plt.title(f"Odcinki nachodzą na siebie od punktu ({zd(poczatek[0])}, {zd(poczatek[1])}) do punktu ({zd(koniec[0])}, {zd(koniec[1])}).")
        # Jeśli odcinki się przecinają, funkcja przeciecie zwróciła tylko współrzędne punktu przecięcia, czyli 2 liczby.
        else:
            plt.scatter(*wspolrzedne, color="red", marker="x", s=200, zorder=3, label=f"Punkt przecięcia ({zd(wspolrzedne[0])}, {zd(wspolrzedne[1])})")
            plt.title(f"Odcinki przecinają się w punkcie ({zd(wspolrzedne[0])}, {zd(wspolrzedne[1])})")
    # Jeśli funkcja przeciecie zwróciła None, odcinki nie przecinają się, ani nie nachodzą na siebie.
    else:
        plt.title("Odcinki się nie przecinają i nie nachodzą na siebie.")

    # Konfiguracja wykresu
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlabel("x")
    plt.ylabel("y")

    # Wykres zapisujemy go do bufora i konwertujemy na Base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    wykres_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return wykres_base64
