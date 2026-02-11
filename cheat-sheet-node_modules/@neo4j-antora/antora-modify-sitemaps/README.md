# antora-modify-sitemaps

Use the `antora-modify-sitemaps` extension to modify the default Antora sitemap generation.

## Usage

Add the extension in a playbook

```
antora:
  extensions:
  - require: "@neo4j-antora/antora-modify-sitemaps"
    sitemap_version: '1.0'
    sitemap_loc_version: 'current'
    move_sitemaps_to_components: true
    data:
      components:
        my-component: 'my-version'
```

## Configuration

### sitemap_version

Optional.

Specifies a version that will be used for the sitemap for all components in the site catalog. If you do not provide a value, by default the version that Antora considers to be the latest version for a given component is used. For details on how Antora determines the 'latest' version, see [Antora version ordering rules](https://docs.antora.org/antora/latest/how-component-versions-are-sorted/#determine-version-order).

You might want to override this value if, for example, you publish prerelease or preview documentation of a component but you do not mark it as `prerelease: true` in the component descriptor (`antora.yml`).

If you are generating output for a single component you can use `sitemap_version` to specify the version of that component that you want to generate a sitemap for. If you are generating output for multiple components, you need to override this value for specific components by using the `data` property.

### sitemap_loc_version

Optional. The default value is `current`.

If this is specified, the paths in the entries in each generated sitemap file are updated by replacing the version as it appears in the path with the value of `sitemap_loc_version`.

For example, with `sitemap_loc_version: 'current'`

```
<loc>https://example.com/my-component/my-version/path/to/page/</loc>
```

is updated to:

```
<loc>https://example.com/my-component/current/path/to/page/</loc>
```

**Note:** If your content is versionless only, you do not need to specify a value for sitemap_loc_version, and any value you do specify is ignored for any versionless content.

### move_sitemaps_to_components

Optional. The default value is `true`.

The sitemap for each component will be moved to _site/\<component>/\<sitemap_version>/sitemap.xml_ unless this attribute is set to `false`.

### data

Optional.

If you want to generate a sitemap from a component by using a version that is not the latest version (as determined by Antora), you can specify the components and versions with this option.

For example, if you have a component, `my-component` and your playbook will generate output for versions `1.0` and `1.1`, you can generate a sitemap for the `1.0` content at _my-component/1.0/sitemap.xml_ with the following:

```
 data:
      components:
        my-component: '1.0'
```
