# TSOHA-workoutplanner

Treeniohjelman suunnittelusovellus

- Käyttäjä voi luoda tunnuksen ja kirjautua sisään ja ulos
- Sovelluksessa on valmis kirjasto liikkeistä, joita voi valita omaan treeniohjelmaan
- Käyttäjä voi luoda oman treeniohjelman, joissa jokaisen liikkeen kohdalle saa asetettua sarjojen ja toistojen määrän, painon ja taukojen pituudet
- Käyttäjä voi seurata omaa kehitystään


Välipalautus 2:

- Käyttäjä voi kirjautua sisään testitunnuksilla, käyttäjänimi: "testuser" salasana "testpassword"
- Sivulla on lyhyt lista liikkeistä, joita ei voi kuitenkaan vielä tutkailla
- Käyttäjän on oltava kirjauduttuna sisään nähdäkseen profiilisivun
- Profiilisivulta pääsee kirjautumaan ulos
- Ei vielä muita toimintoja, ja ulkoasu on testivaiheessa


Välipalautus 3:

- Käyttäjä voi tehdä itselleen käyttäjätunnuksen ja kirjautua sisään ja ulos
- Käyttäjä voi tehdä itselleen treeniohjelman valitsemalla ensin liikkeet, seuraavalla sivulla settien määrät ja ohjelman nimen, ja lopuksi toistojen ja painojen määrän.
- Käyttäjä voi tarkastella treeniohjelmaa tai poistaa sen kokonaan
- Mikäli käyttäjä ei viimeistele ohjelmaa luontivaiheessa painamalla tallenna, se poistuu tietokannasta
- Ohjelmia ei voi (vielä) muokata, eikä ohjelman keskeyttämisestä tai poistamisesta tule (vielä) mitään varoitusta
- Sivulla on lista liikkeistä, joka on vielä testausvaiheessa, eikä siitä voi tarkastella yksityiskohtia
- Ulkoasu on yhä testausvaiheessa


Loppupalautus:

- Käyttäjä voi luoda tunnuksen ja kirjautua sisään ja ulos
- Sovelluksessa on valmis kirjasto liikkeistä, joita voi valita omaan treeniohjelmaan (ei kuitenkaan tällä sivulla). Liikkeistä näkee yksityiskohtia 'Details'-napin takaa
- Käyttäjä voi luoda oman treeniohjelman, joissa jokaisen liikkeen kohdalle saa asetettua sarjojen, toistojen ja painojen määrän
- Käyttäjä voi tarkastella treeniohjelmaa tai poistaa sen kokonaan
- Mikäli käyttäjä ei viimeistele ohjelmaa luontivaiheessa painamalla tallenna, se poistuu tietokannasta
- Käyttäjä voi muokata treeniohjelmiaan
- Käyttäjä voi kirjata treeniohjelman tehdyksi, jolloin se ilmestyy profiiliin kohtaan "Completed workouts". Sieltä käyttäjä näkee  kaikki kirjatut treenit.
- Käyttäjä voi poistaa kirjatun treenin


Käynnistysohjeet paikalliseen käyttöön:

- Kloonaa repositorio koneellesi ja siirry sen juurikansioon
- luo kansioon .env -tiedosto, ja määritä sen sisältö seuraavanlaiseksi:
    DATABASE_URL = <tietokannan-paikallinen-osoite>
    SECRET_KEY = <salainen-avain>

    Seuraavaksi aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komennoilla

    $ python3 -m venv venv

    $ source venv/bin/activate

    $ pip install -r ./requirements.txt

    Nyt voit käynnistää sovelluksen komennolla

    $ flask run