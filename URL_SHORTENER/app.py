from urllib.parse import urlencode
from urllib.request import urlopen

def short_url(url):
    request_url = 'http://tinyurl.com/api-create.php?' + urlencode({'url': url})
    with urlopen(request_url) as response:
        return response.read().decode('utf-8')

def main():
    while True:
        url = input("Enter a URL (or 'q' to quit): ")
        if url.lower() == 'q':
            break
        shortened_url = short_url(url)
        print("Shortened URL:", shortened_url)

if __name__ == '__main__':
    main()
