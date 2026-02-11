# antora-page-roles

Adds classes to the `<body>` tag of a page, based on roles specified before the document header.

Use any valid asciidoc format:

* `[role="role-one role-two"]`
* `[role=role-one role-two]`
* `[.role-one.role-two]`

**Note:** Any roles specified in this way are overwritten by the values in the `:page-role:` header attribute if it is present.