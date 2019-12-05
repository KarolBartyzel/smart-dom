# smart-dom - opis kodu

## Mobile
* Folder screens - zawiera definicje 2 głównych ekranów nawigatora
  * HistoryScreen - ekran z historią
  * OrdersScreen - ekran interakcji z użytkownikiem
* Folder components - zawiera definicje komponentów użytych w ekranach
  * CommandRecognizer - komponent wyświetla informację o rozpoznawaniu komendy i obsługuję komunikację z serwerem
  * CommandSummary - komponent wyświetla informację o zakończonym poleceniu i jego powodzeniu (lub nie)
  * FadeInView - komponent wyświetlający ruchomy mikrofon
  * VoiceRecognizer - komponent wyświetla informację o rozpoznawaniu mowy i obsługuje komunikację z lambdą Firebase, która rozpoznaje mowę

## Lamda Firebase (FaaS)
* Folder backend/functions
  * index.js - funkcje speechToText i textToSpeech - zamiana tekstu w głos i w drugą stronę

## Serwer
* Folder backend/python
  * num_to_words - przerobiona biblioteka, ktora przekształca liczebnik w słowną reprezentację (dorobiona obsługa liczebników porządkowych)
  * run.cmd - skrypt do instalacji pakietów i uruchomienia serwera
  * server.py
    * wczytuje plik konfiguracyjny
    * preprocesuje dane z pliku, oblicza słownik słów itp.
    * definiuje endpoint, który koordynuje wywołania pozostałych modułów w reakcji na zapytanie z transkrypcją
  * resolve_command.py
    * KeyedVectors ładuję plik w2v dla języka polskiego
    * command_map - definicja słów na jakie tłumaczą się komendy
    * command_value_map - definicja słów na jakie tłumaczą się nieliczbowe wartości dla komend
    * pos_map - mapa możliwych tagów w w2v
    * lev_edits1, lev_edits2, levenshtein - wyznaczają słowa odległe o odpowiednio 1,2 oraz 1 i 2
    * calculate_compliance - oblicza rozmiar przecięcia 2 wektorów słów
    * tag_sentence, lemmatize_sentence - wyznacza lematy dl
    * find_room_setup - preprocesuje dane dla pokojów
    * find_room - znajduje pokoje najbardziej pasujące do tekstu wejściowego
    * find_device_setup - preprocesuje dane dla urządzeń
    * find_device - znajduje urządzenia najbardziej pasujące do tekstu wejściowego
    * find_command_setup - preprocesuje dane dla komend
    * find_command - znajduje komendy najbardziej pasujące do tekstu wejściowego
    * find_command_value_setup - preprocesuje dane dla wartości komend złożonych
    * find_command_values - znajduje wartości komend złożonych najbardziej pasujące do tekstu wejściowego
    * create_result - przekształca zebrane informację w ostateczną komendę i loguje informacje o wynikach
    * resolve_command - zarządza wykonaniem pozostałych funkcji w celu uzyskania ostatecznej komendy na podstawie tekstu
    
  * apply_command.py
    * definiuje klasę Radio, która obsługuje api VLC
    * definiuje akcje wykonywane dla urządzenia A3 (radio - piosenka na moim laptopie) w zależności od komendy, która przyszła
