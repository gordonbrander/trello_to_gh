# Mustache template for issue body
ISSUE_TEMPLATE = """{{desc}}

(Exported from Trello {{url}})

{{#actions}}
---

On {{date}}, @{{memberCreator.username}} wrote:

{{data.text}}

{{/actions}}
"""