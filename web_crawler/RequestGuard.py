import re

import bs4, requests
from urllib.parse import urlparse

class RequestGuard:

    def __init__(self, url):
        """
        Initializes the RequestGuard with a target domain.
        Extracts the network location and fetches the domain's robots.txt rules
        to establish scraping boundaries.
        """
        parsed = urlparse(url)
        self.domain = parsed.netloc
        self.forbidden = self.parse_robots()

    def parse_robots(self):
        """
        Fetches and parses the target domain's robots.txt file.
        Uses regular expressions to extract and return a list of paths
        explicitly disallowed by the host.
        """
        url = f'https://{self.domain}/robots.txt'
        t = requests.get(url)
        soup = bs4.BeautifulSoup(t.text, features="html.parser")
        forbidden = re.findall(r'Disallow: (.+)', t.text)
        return forbidden

    def can_follow_link(self, url):
        """
        Evaluates a given URL against the stored domain and robots.txt rules.
        Returns a boolean indicating whether the URL is within the target domain
        and permitted for traversal.
        """
        parsed = urlparse(url)
        domain1 = parsed.netloc
        path = parsed.path
        if domain1 == self.domain:
            for block in self.forbidden:
                if re.findall(rf'^{block}', path):
                    return False
            return True
        else:
            return False


    def make_get_request(self, url, use_stream=False):
        """
        Executes an HTTP GET request after validating the URL against network constraints.
        Supports stream toggling for large payloads.
        Returns the response object or None if the URL is restricted.
        """
        if self.can_follow_link(url):
            return requests.get(url, stream=use_stream)
        else:
            return None