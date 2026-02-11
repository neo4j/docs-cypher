# antora-add-notes

Use the `antora-add-notes` extension to add asciidoc into the top of pages.

The extension uses [Page Attributes](https://docs.antora.org/antora/2.3/page/page-attributes/) to define content to be added to the top of a page, immediately below the title.

## Usage

Define attributes in an Antora playbook, _antora.yml_, or asciidoc page header.

### page-add-notes-module

Use the `page-add-notes-module` attribute to specify the name of the module that contains the asciidoc you want to add. If `page-add-notes-module` is not specified, the `ROOT` module is used.

```
page-add-notes-module: my-notes@
```

### page-add-notes-tags

```
page-add-notes-tags: tag-1;tag-2@
```

Tagged sections are read from `{page-add-notes-module}:partial$/notes.adoc`.

To include multiple tags, add the tags as a list, for example `page-add-notes-tags: review;preview`.


### page-add-notes-versions

By default the note is displayed in all versions of all pages.
Use the `page-add-notes-versions` attribute to specify which versions of the HTML pages you want the note to be displayed on.
If you do not include this attribute, notes will be added to pages in all versions. 

```
page-add-notes-versions: ['5', '4.4']
```

## Example

1. Create _modules/my-notes/partials/notes.adoc_ with the following content:

    ```
    # tag::preview[]
    [NOTE]
    ====
    This is preview content
    ====
    # end::preview[]
    ```

2. In your Antora playbook file, add an asciidoc attribute - `page-add-notes-module: my-notes`
3. In your Antora playbook file, add an asciidoc attribute - `page-add-notes-tags: preview`
3. Use Antora to generate HTML.