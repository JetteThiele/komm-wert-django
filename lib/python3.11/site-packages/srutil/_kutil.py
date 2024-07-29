import requests
import wikipedia
from bs4 import BeautifulSoup as Bs


class KnowledgeUtil:
    @staticmethod
    def briefoflinuxcmd(cmd: str):
        """
        this functions provide response by scraping the web-contents.

        response may contain html elements
        """
        params = {"cmd": cmd}
        response = requests.get(url="https://explainshell.com/explain", params=params)
        soup = Bs(response.text, parser="html.parser", features="lxml")
        cmd_contents = list()
        for i in range(25):
            if soup.find("pre", attrs={"id": "help-" + str(i)}) is not None:
                cmd_contents.append(soup.find("pre", attrs={"id": "help-" + str(i)}).contents)
        return cmd_contents

    @staticmethod
    def searchwiki(title: str):
        title = list(wikipedia.search(title)).pop(0)
        return wikipedia.summary(title)
