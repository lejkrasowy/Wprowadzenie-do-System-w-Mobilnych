# Lab 02 – Implementacja symulatora stacji bazowej

## Co zostało zrealizowane
Zaimplementowano symulator stacji bazowej w języku Python w klasie BaseStationSimulator.
Uruchomienie programu wywołuje okno interfejsu w którym użytkownik może ustawić odpowiednie parametry a potem rozpocząc symulację. Pokazuje aktulizujące się w czasie rzeczywistym informacje dotyczące bazy wliczając liczbę obsłużonych,, status kanałów, status kolejki i pozostałe dane.
Po przekroczeniu limitu czasu symulacji, symulacja się kończy, wyświetlając wykresy dotyczące zapełnienia kanałów, kolejki oraz zapisuje wynik symulacji do pliku pod nazwą "wyniki_naszej_symulacji.txt".

## Uruchomienie
Plik Lab02.py powinien zostać uruchomiony przez interpreter Pythona wraz z zainstalowanym pakietem matplotlib.

## Trudności / refleksja (opcjonalnie)
Zbyt mała intensywność powoduje brak powstawania kolejki.
