import typer

from pathlib import Path
from articular import ArticularSourceDocument
from scaffy import ScaffyDocument, ScaffyDataset, ScaffyQuery
from tqdm import tqdm
from rdflib import ConjunctiveGraph, Dataset


app = typer.Typer()


def get_recursively(search_dict, field):
    fields_found = []
    for key, value in search_dict.items():
        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


def save(path: Path, data: str):
    with open(path, 'w') as out_file:
        out_file.write(data)


@app.command()
def init():
    ...


def query(graph: Dataset):
    paths = Path().glob('query/**/*.rq')

    for path in paths:
        with open(path, 'r') as in_file:
            query = in_file.read()

        result = graph.query(query)
        representation = ScaffyQuery(title=str(path), result=result)

        site = Path('site')
        query = site / 'query'
        query.mkdir(parents=True, exist_ok=True)

        resource = Path(path.relative_to('query').stem)
        save(query / resource.with_suffix('.html'), representation.html)


@app.command()
def build():
    references_map = {}
    results = {}
    sources = {}
    # graph = ConjunctiveGraph()
    graph = Dataset()
    paths = Path().glob('document/**/*.md')
    for path in tqdm(paths):
        # relative_path = path.relative_to('document')
        with open(path, 'r') as in_file:
            source = ArticularSourceDocument(in_file.read(), name=str(path))

        sources[path] = source
        result = source.transform()
        results[path] = result

        references = []
        for item in result.json.get('@graph', []):
            if isinstance(item, dict):
                ids = get_recursively(item, '@id')
                # Remove blank nodes.
                ids = [item for item in ids if not item.startswith('_:')]
                for ref in ids:
                    references.append(ref)

        key = str(path)
        if key in references_map:
            references_map[key] = list(set(references_map[key].extend(references)))
        else:
            references_map[key] = references

    for path in results:
        source = sources[path]
        result = results[path]
        for q in result.graph.quads():
            graph.add(q)

        local_references = { 
            str(Path(k).relative_to('document').with_suffix('.html')) : v 
            for k, v in references_map.items()
            if v and k != str(path) 
        }

        site = Path('site')
        data = site / 'data'
        page = site / 'page'
        document = site / 'document'
        data.mkdir(parents=True, exist_ok=True)
        page.mkdir(parents=True, exist_ok=True)
        document.mkdir(parents=True, exist_ok=True)
        resource = Path(path.relative_to('document').stem)

        serialisations = {
            '.ttl': 'turtle',
            '.nq': 'nquads',
            '.nt': 'ntriples',
            '.trig': 'trig'
        }

        data_paths = {
            data / resource.with_suffix(key) : value
            for key, value in serialisations.items()
        }
        data_paths[data / resource.with_suffix('.json')] = 'json-ld'

        representation = ScaffyDocument(
            document=result,
            representations=data_paths,
            references=local_references
        )

        save(page / resource.with_suffix('.html'), representation.html)
        save(data / resource.with_suffix('.json'), representation.document.json_ld)
        for extension, serialisation in serialisations.items():
            save(
                path=data / resource.with_suffix(extension),
                data=result.graph.serialize(format=serialisation)
            )

    summary = { 
        str(Path(path).relative_to('document').with_suffix('.html')) : len(result.graph)
        for path, result in results.items()
    }

    queries = [str(Path(path).relative_to('query').with_suffix('.html')) for path in Path().glob('query/**/*.rq')]
    dataset_representation = ScaffyDataset(summary, queries=queries)
    save(page / 'dataset.html', dataset_representation.html)

    save(data / 'dataset.trig', graph.serialize(format='trig'))
    save(data / 'dataset.nq', graph.serialize(format='nquads'))

    query(graph)
