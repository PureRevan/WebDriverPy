"""
Just some random URLs for testing purposes

Test the URLs and print a list of function URLs by running this file

The implementation of the test can be seen below at the main entry point
"""

test_urls = ['https://google.de', 'https://youtube.com', 'https://amazon.de', 'https://wikipedia.org',
             'https://facebook.com', 'https://twitter.com', 'https://instagram.com', 'https://linkedin.com',
             'https://reddit.com', 'https://netflix.com', 'https://ebay.de', 'https://spiegel.de', 'https://zeit.de',
             'https://bild.de', 'https://theguardian.com', 'https://bbc.com', 'https://cnn.com', 'https://nytimes.com',
             'https://stackoverflow.com', 'https://github.com', 'https://microsoft.com', 'https://apple.com',
             'https://play.google.com', 'https://soundcloud.com', 'https://spotify.com', 'https://twitch.tv',
             'https://aliexpress.com', 'https://booking.com', 'https://airbnb.com', 'https://imdb.com',
             'https://rottentomatoes.com', 'https://hulu.com', 'https://pinterest.com', 'https://tumblr.com',
             'https://wordpress.com', 'https://blogspot.com', 'https://medium.com', 'https://quora.com',
             'https://yahoo.com', 'https://bing.com', 'https://duckduckgo.com', 'https://archive.org',
             'https://pbs.org', 'https://nationalgeographic.com', 'https://nasa.gov', 'https://weather.com',
             'https://accuweather.com', 'https://wunderground.com', 'https://bbc.co.uk', 'https://thelocal.de',
             'https://dw.com', 'https://thelocal.fr', 'https://marca.com', 'https://elpais.com',
             'https://as.com', 'https://sueddeutsche.de', 'https://faz.net', 'https://zeit.de', 'https://taz.de',
             'https://n-tv.de', 'https://rtl.de', 'https://ard.de', 'https://zdf.de', 'https://tagesschau.de',
             'https://faz.net', 'https://heise.de', 'https://chip.de', 'https://computerbild.de', 'https://golem.de',
             'https://spiegel.de', 'https://focus.de', 'https://stern.de', 'https://n24.de', 'https://rbb24.de',
             'https://ntv.de', 'https://dw.com', 'https://srf.ch', 'https://20min.ch', 'https://blick.ch',
             'https://tagesanzeiger.ch', 'https://letemps.ch', 'https://tdg.ch', 'https://bluewin.ch',
             'https://telegraph.co.uk', 'https://independent.co.uk', 'https://guardian.co.uk', 'https://thetimes.co.uk',
             'https://ft.com', 'https://bbc.co.uk', 'https://mirror.co.uk', 'https://sky.com', 'https://channel4.com',
             'https://bbc.com', 'https://nytimes.com', 'https://usatoday.com', 'https://reuters.com',
             'https://apnews.com', 'https://bloomberg.com', 'https://wsj.com', 'https://forbes.com',
             'https://fortune.com', 'https://businessinsider.com', 'https://cnbc.com', 'https://marketwatch.com',
             'https://economist.com', 'https://huffpost.com', 'https://buzzfeed.com', 'https://vice.com',
             'https://mashable.com', 'https://engadget.com', 'https://techcrunch.com', 'https://arstechnica.com',
             'https://wired.com', 'https://slashdot.org', 'https://thenextweb.com', 'https://tomsguide.com',
             'https://pcmag.com', 'https://cnet.com', 'https://gizmodo.com', 'https://lifehacker.com',
             'https://digitaltrends.com', 'https://androidcentral.com', 'https://macrumors.com', 'https://imore.com',
             'https://9to5mac.com', 'https://androidauthority.com', 'https://linux.com', 'https://stackexchange.com',
             'https://superuser.com', 'https://askubuntu.com', 'https://unix.stackexchange.com',
             'https://serverfault.com', 'https://dba.stackexchange.com', 'https://stackoverflow.com'
             ]


def main():
    global test_urls

    """
    Testing to remove non functioning URLs
    """
    import requests
    from thread_manager import ThreadManager

    def test_urls_task(url: str):
        global test_urls

        try:
            requests.get(url, timeout=5)
        except requests.exceptions.RequestException:
            test_urls.remove(url)

    ThreadManager(test_urls_task, [(url,) for url in test_urls.copy()]).join()
    print(test_urls)


if __name__ == '__main__':
    main()
