from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape

from articular import ArticularResultDocument


env = Environment(
    loader=PackageLoader('scaffy'),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)


class ScaffyBase:

    def __str__(self) -> str:
        return self.result

    @property
    def html(self) -> str:
        return self.soup.prettify()

    @property
    def soup(self) -> BeautifulSoup:
        if not self._soup:
            self._soup = BeautifulSoup(self.result, features='lxml')

        return self._soup


class ScaffyDataset(ScaffyBase):

    _template = env.get_template('dataset.html')

    def __init__(self, summary, queries):
        self._soup = None
        self.result = ScaffyDataset._template.render(summary=summary, queries=queries)


class ScaffyQuery(ScaffyBase):

    _template = env.get_template('query.html')

    def __init__(self, title: str, result):
        self._soup = None
        self.result = ScaffyQuery._template.render(title=title, result=result)


class ScaffyDocument(ScaffyBase):

    _template = env.get_template('page.html')

    def __init__(self, document: ArticularResultDocument, representations: list | None, references: dict = None) -> None:
        self.document = document
        title = document.json.get('@id')
        self.graph = document.json.get('@graph', [])
        self.result = ScaffyDocument._template.render(
            title=title,
            graph=self.graph,
            representations=representations,
            references=references
        )
        self._soup = None

