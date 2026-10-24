"""Entity identity, visible FAQ fidelity and conditional article schema regression."""
import json
from pathlib import Path
import re
import sys

from chronicles_lib.faq import faq_schema
from chronicles_lib.model import load_all_articles
from chronicles_lib.build import render_article_page

ROOT = Path(__file__).resolve().parents[1]


def blocks(page):
    return [json.loads(s) for s in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', page, re.S)]


def main():
    home = (ROOT / 'index.html').read_text(encoding='utf-8')
    org = next(s for s in blocks(home) if s.get('@type') == 'Organization')
    assert org['@id'] == 'https://lonkodigital.com/#organization'
    assert org['sameAs'] == [
        'https://www.linkedin.com/company/143083521',
        'https://www.facebook.com/LonkoDigital',
        'https://www.instagram.com/lonkodigital/',
    ]
    assert 'founder' not in org
    about = (ROOT / 'about/index.html').read_text(encoding='utf-8')
    for page in [home, about]:
        assert not any('"@type": "Person"' in json.dumps(s) for s in blocks(page))
        assert not re.search(r'\bAlex\b', page)
    main_html = re.search(r'<main\b.*?</main>', about, re.S).group()
    assert main_html.count('<h1 ') == 1
    assert '\u2014' not in main_html
    actual = next(s for s in blocks(about) if s.get('@type') == 'FAQPage')
    assert actual == faq_schema(main_html)
    assert len(actual['mainEntity']) == 3
    # Static Insights pages must also match visible FAQs if an approved package
    # introduces one; no FAQ markup should appear on an ordinary article.
    for path in (ROOT / 'insights').rglob('index.html'):
        page = path.read_text(encoding='utf-8')
        main = re.search(r'<main\b.*?</main>', page, re.S)
        expected = faq_schema(main.group()) if main else None
        observed = [s for s in blocks(page) if s.get('@type') == 'FAQPage']
        assert observed == ([expected] if expected else []), path
    assert faq_schema('<h2>Ordinary section</h2><h3>Question?</h3><p>Answer.</p>') is None
    assert faq_schema('<section hidden><h2>FAQ</h2><h3>Hidden?</h3><p>Hidden answer.</p></section>') is None
    assert faq_schema('<section aria-hidden="true"><h2>FAQ</h2><h3>Hidden?</h3><p>Hidden answer.</p></section>') is None
    assert faq_schema('<h2>FAQ</h2><h3>Visible?</h3><p>Yes.<span style="display:none">Excluded.</span></p>')['mainEntity'][0]['acceptedAnswer']['text'] == 'Yes.'
    fixture = '<h2>FAQ</h2><h3>Question?</h3><p>A <a href="/">linked</a> answer.</p><p>Second paragraph.</p><h2>Other</h2><p>Excluded.</p>'
    result = faq_schema(fixture)
    assert result['mainEntity'][0]['acceptedAnswer']['text'] == 'A linked answer. Second paragraph.'
    try:
        faq_schema('<h2>FAQ</h2><h3>No answer?</h3><h2>Next</h2>')
    except ValueError:
        pass
    else:
        raise AssertionError('Incomplete FAQ must fail closed')
    corpus = load_all_articles(ROOT / 'chronicles/content')
    for article in corpus:
        rendered = render_article_page(article, corpus)
        schemas = blocks(rendered)
        assert schemas[0]['@type'] == article.schema_type
        assert not any(s.get('@type') == 'FAQPage' for s in schemas)
    article = corpus[0]
    article.body += '\n\n## Frequently asked questions\n\n### Is this visible?\n\nYes, this exact answer.\n'
    generated = next(s for s in blocks(render_article_page(article, corpus)) if s.get('@type') == 'FAQPage')
    assert generated['mainEntity'][0]['name'] == 'Is this visible?'
    assert generated['mainEntity'][0]['acceptedAnswer']['text'] == 'Yes, this exact answer.'
    print('ENTITY / VISIBLE FAQ FIDELITY / CONDITIONAL ARTICLE SCHEMA: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
