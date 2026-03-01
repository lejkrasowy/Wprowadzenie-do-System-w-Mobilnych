import matplotlib.pyplot as plot
import math

dane = []
a = 16807
b = 0
c = 2147483647
aktualne_ziarno = 1

def ustaw_ziarno(ziarno):
    global aktualne_ziarno
    if ziarno is not None:
        aktualne_ziarno = ziarno
    else:
        aktualne_ziarno = 12345

def Genu():
    global aktualne_ziarno
    aktualne_ziarno = (a * aktualne_ziarno) % c
    return aktualne_ziarno / c

def generuj_poissona(lam, ilosc_liczb):
    dane = []
    q = math.exp(-lam)

    for i in range(ilosc_liczb):
        x = -1
        s = 1.0
        while s > q:
            u = Genu()
            s = s * u
            x = x + 1
        dane.append(x)
    return dane

def generuj_normalny(mu, sigma, ilosc_liczb):
    dane = []
    for i in range(ilosc_liczb):
        u1 = Genu()
        u2 = Genu()
        zo = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        x = mu + sigma * zo
        dane.append(x)
    return dane

ilosc = 100000
ustaw_ziarno(42)
dane_poisson = generuj_poissona(lam=5, ilosc_liczb=ilosc)
dane_normalny = generuj_normalny(mu=10, sigma=2, ilosc_liczb=ilosc)

plot.figure(1)
plot.title('Rozkład Poissona (lambda=5)')
plot.hist(dane_poisson, bins=15, edgecolor='black')
plot.xlabel('Wartość')
plot.ylabel('Liczba wystapień')
plot.figure(2)
plot.title('Rozkład Normalny (mu=10, sigma=2)')
plot.hist(dane_normalny, bins=100, edgecolor='black', color='red')
plot.xlabel('Wartość')
plot.ylabel('Liczba wystapień')
plot.show()