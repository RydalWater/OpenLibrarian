# OpenLibrarian
Open Librarian is a website for tracking and sharing a love of books. It utilizes the Nostr protocol so that users can bring their friends and social connections with them, and take them elsewhere if they'd like to. 

## Goals
- To broaden the specific application base of the Nostr network and allow/encourage specialisation to take place 
- Make a fun, easy to use book tracking app which includes:
  - Library shelves
  - Personal reading challenges
  - Book reviews
  - Reading progress
  - Book-related social groups


## Open Source Stack
Open Librarian is built on a range of Free and Open Source Software (FOSS) projects, the most prominent of which are:

- [Open Library](https://openlibrary.org/) - A project working on making all the published works of humankind available to everyone
- [rust-nostr](https://rust-nostr.org/) - A Nostr development kit built in rust with a range of language bindings 
- [Django](djangoproject.com) - A web-application framework written in python
- [Bootstrap](https://getbootstrap.com/) - A front-end toolkit


## Nostr Objects
There are a range of Nostr objects underpinning this application which manage the data structures.

Note that any objects still to be implemented are to be considered a WIP and may be subject to substantial change prior to implementation.

### User’s Shelves (Implemented)

```json
{
  ‘kind’ : 30003,
  ‘tags’ : [
    ‘d’           : <SHA-1 of (pubkey + list ID)>,
    ‘title’       : <list Title>,
    ‘description’ : <list description>,
    ‘i’           : <‘isbn:’ + isbn of book>,
    …
  ],
  ‘content’ : <‘Books & Literature (OpenLibrarian)’ + ‘:’ + # of hidden books + ‘:’ + NIP04 encrypted ‘i’ tags for isbns of hidden books>   
}
```

List IDs include: CR, HR, TRW, TRS


### Book Review - Individual (to be implemented)

```json
{
  ‘kind’ : 3xxxx,
  ‘tags’ : [
    ‘d’      : <‘isbn:’ + isbn of book OR, ‘h:’ + NIP04 encrypted isbn of book>
    ‘k’      : <NIP 73 external content k tag for books i.e., ‘isbn’>
    ‘rating’ : <normalised value between 0 and 1, optional mark>
    ‘raw’    : <optional raw rating value X/Y (e.g 5/10)>
  ],
  ‘content’ : ‘’
}
```

### Book Review - Set (to be implemented)

```json
{
  ‘kind’ : 30020,
  ‘tags’ : [
    ‘d’ : <SHA-1 of (pubkey + ‘OLR’)>
    ‘a’ : <coordinates to review events>,
    …
  ],
  ‘content’ : ‘’
}
```

### Book Progress - Individual (to be implemented)

```json
{
  ‘kind’ : 3xxxx,
  ‘tags’ : [
    ‘d’       : <‘isbn:’ + isbn of book OR, ‘h:’ + NIP04 encrypted isbn of book>
    ‘k’       : <NIP 73 external content k tag for books i.e., ‘isbn’>
    ‘current’ : <numerator>
    ‘max’     : <denominator>
    ’unit’    : <units; “%”, “pages” or “min”>
    ‘start’   : <unix timestamp of start date OR ‘NA’>,
    ‘end’     : <unix timestamp of end date OR ‘NA’>
  ],
  ‘content’ : ‘’
}
```

### Reading Progress  - Set (to be implemented)

```json
{
  ‘kind’ : 3xxxx,
  ‘tags’ : [
    ‘d’ : <SHA-1 of (pubkey + ‘OLP’)>
    ‘a’ : <coordinates to progress events>,
    …
  ],
  ‘content’ : ‘’
}
```

**Notes:**

- Reviews only available for completed books
- Progress only available for ‘Currently Reading’, if book is moved to ‘Have Read’ then progress automatically set to 100% (or equivalent)
- If book is moved onto ‘Currently Reading’ or ‘Want to Read’ shelves then progress is reset at 0% (or equivalent) along with start and end dates if already available

### Installation and Development

Clone the repository into a suitable local location 

```
git clone ‘https://github.com/RydalWater/OpenLibrarian.git’
```

Navigate to folder and set up virtual env.

```
cd OpenLibrarian

python -m venv env
```

Activate env if Linux/Mac

```
source ./env/bin/activate
```

Activate env is Windows

```
./env/Scripts/activate
```

Install relevant python libraries.

```
cd openlibrarian_root

pip install -r requirements.txt
```

Rename/modify the .example_env file as follows:

- Remove ‘example_’ from the name
- Generate a new npub/nsec key pair for Nostr testing purposes
- Default relays list (if you want to change this)

Modify settings.py (in ‘openlibrarian_root/openlibrarian/‘)

- Comment out:
  - `ALLOWED_HOSTS = os.getenv(…)`
  - `DEBUG = os.getenv(…)`
  - `SECRET_KEY = os.getenv(…)`
- Uncomment the following: 
  - `ALLOWED_HOSTS = […]`
  - `DEBUG = True`
  - `SECRET_KEY = ‘SUPERsecretKEY123abc’`

Note that these parameters are simply for testing/development purposes. Further updates will be required if you plan on deploying to a production environment.

Start the local server (from the openlibrarian_root folder)

```
python manage.py runserver
```

That is it, you should now see a message similar to the one below in the console. You may get a warning about migrations. Normally for a django project you would rerun the `python manage.py makemigrations && python manage.py migrate` commands, however this project does not use any backend database so this shouldn’t be necessary.

```
Django version 5.0.8, using settings ‘openlibrarian.settings’
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```




