# Lyrically

Lyrically is a Python-based tool designed to streamline the collection and organization of artist lyrics.

## Description

Lyrically is a Python tool aimed at simplifying the collection and organization of song lyrics. By inputting an artist's name, users can efficiently retrieve, store, and manage lyrics for personal analysis or enjoyment. The tool caters to music enthusiasts and researchers alike, providing a streamlined approach to exploring and archiving the lyrical world of their favorite artists.

## Getting Started

### Dependencies

* Python
* beautifulsoup4
* bs4
* certifi
* charset-normalizer
* idna
* requests
* soupsieve
* urllib3

### Installing

* Python can be downloaded from [here](https://www.python.org/).
* Install dependencies using `pip install -r requirements.txt` stored in main project directory.
* If you're using proxies, add the proxies to the file in `storage/proxies`.

### Executing program

* Creating an instance of Lyrically
```
from lyrically import Lyrically

def main():
    lyrically = Lyrically(use_proxies = False)
    lyrically.setup()

if __name__ == "__main__":
    main()
```

* Getting an artist's lyrics
```
from lyrically import Lyrically

def main():
    lyrically = Lyrically(use_proxies = False)
    lyrically.setup()

    artist_name = "Taylor Swift"
    lyrically.get_artist_songs(artist_name)

if __name__ == "__main__":
    main()
```

## Help

* All runtime data of Lyrically are stored in the log file located at `storage/logs/lyrically.log`.

## Authors

Contributors

* [Filming](https://github.com/filming)

## License

This project is licensed under the MIT License - see the LICENSE file for details
