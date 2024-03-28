from articular import ArticularResultDocument
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(
    loader=PackageLoader('scaffy'),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)


class ScaffyBase:

    def __init__(self, template_path: str) -> None:
        self._pretty_html = None
        self._soup = None
        self._template = env.get_template(template_path)

    def __str__(self) -> str:
        return self.result

    @property
    def html(self) -> str:
        if not self._pretty_html:
            self._pretty_html = self.soup.prettify()

        return self._pretty_html

    @property
    def soup(self) -> BeautifulSoup:
        if not self._soup:
            self._soup = BeautifulSoup(self.result, features='lxml')

        return self._soup

    def render(self, **kwargs) -> str:
        return self._template.render(**kwargs)


class ScaffyDataset(ScaffyBase):

    def __init__(self, summary, queries):
        super().__init__('dataset.html')
        self.result = self.render(summary=summary, queries=queries)


class ScaffyQuery(ScaffyBase):

    def __init__(self, title: str, result):
        super().__init__('query.html')
        self.result = self.render(title=title, result=result)


class ScaffyDocument(ScaffyBase):

    def __init__(self, document: ArticularResultDocument, representations: list | None, references: dict = None) -> None:
        super().__init__('page.html')
        self.document = document
        self.result = self.render(
            title=document.json.get('_title'),
            graph=document.json.get('@graph', []),
            representations=representations,
            references=references
        )
