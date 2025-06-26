from jinja2 import Template

s = "{{payload.articles[_n_].description}}"
context = {
    "payload": {
        "articles": [
            {"description": "This is the first article."},
            {"description": "This is the second article."},
            {"description": "This is the third article."}
        ]
    },
    "_n_": 0
}
template = Template(s)
for _n_ in range(3):
    context["_n_"] = _n_
    result = template.render(context)
    print(f"Result for _n_={_n_}: {result}")
# Output should be:
# Result for _n_=0: This is the first article.
# Result for _n_=1: This is the second article.
# Result for _n_=2: This is the third article.