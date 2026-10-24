"""FAQ schema derived exclusively from visible, explicitly headed FAQ content."""

from html.parser import HTMLParser
import re


class _FAQParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.heading = None
        self.heading_text = []
        self.active = False
        self.question = None
        self.answer = []
        self.items = []
        self.hidden_tags = []

    def finish_answer(self):
        if self.question is not None:
            answer = " ".join("".join(self.answer).split())
            # Incomplete or non-question sections must never become FAQ schema.
            if not answer or not self.question.endswith("?"):
                raise ValueError("FAQ questions require visible questions and answers")
            self.items.append({
                "@type": "Question", "name": self.question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            })
        self.question, self.answer = None, []

    def handle_starttag(self, tag, attrs):
        void = tag in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
        attrs = dict(attrs)
        hidden = (tag in {"script", "style", "template"} or "hidden" in attrs
                  or attrs.get("aria-hidden", "").lower() == "true"
                  or re.search(r"(?:display\s*:\s*none|visibility\s*:\s*hidden)",
                               attrs.get("style", ""), re.I))
        if self.hidden_tags or hidden:
            if not void:
                self.hidden_tags.append(tag)
            return
        if re.fullmatch(r"h[1-6]", tag):
            if self.active:
                self.finish_answer()
            self.heading, self.heading_text = tag, []
        elif self.active and tag in {"p", "li", "br"}:
            self.answer.append(" ")

    def handle_endtag(self, tag):
        if self.hidden_tags:
            if tag == self.hidden_tags[-1]:
                self.hidden_tags.pop()
            return
        if tag == self.heading:
            text = " ".join("".join(self.heading_text).split())
            if tag == "h2":
                self.active = text.casefold() in {
                    "faq", "faqs", "frequently asked questions", "quick answers",
                }
            elif tag == "h1":
                self.active = False
            elif tag == "h3" and self.active:
                self.question = text
            elif self.active:
                raise ValueError("FAQ questions must be H3 under an H2 FAQ heading")
            self.heading = None
        elif tag == "section" and self.active:
            self.finish_answer()
            self.active = False
        elif self.active and tag in {"p", "li"}:
            self.answer.append(" ")

    def handle_data(self, text):
        if self.hidden_tags:
            return
        if self.heading:
            self.heading_text.append(text)
        elif self.active and self.question is not None:
            self.answer.append(text)


def faq_schema(html):
    """Return FAQPage only for explicit visible H2/H3 FAQ sections.

    No front-matter FAQ list or generated questions are accepted. Text is taken
    from the same rendered HTML used on the page, preserving inline wording.
    """
    parser = _FAQParser()
    parser.feed(html)
    parser.close()
    parser.finish_answer()
    if not parser.items:
        return None
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": parser.items}
