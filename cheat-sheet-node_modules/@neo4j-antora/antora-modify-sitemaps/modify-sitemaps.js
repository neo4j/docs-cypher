const { posix: path } = require('path')
const semver = require('semver')

module.exports.register = function ({ config }) {

  const pluralize = (count, noun, suffix = 's', plural = '') => {
    if (count !== 1) {
      return plural !== '' ? plural : `${noun}${suffix}`
    }
    return noun
  }

  const SITEMAP_STEM = 'sitemap'
  const SITEMAP_PREFIX = 'sitemap-'
  const SITEMAP_EXT = '.xml'

  const logger = this.getLogger('modify-sitemaps')
  let componentVersions, mappedComponentVersions = {}
  let mappedVersions = {}
  let unMappableComponents = []
  
  this
  .on('navigationBuilt', ({ playbook, contentCatalog }) => {

    const files = contentCatalog.findBy({ family: 'nav' })

    componentVersions = files.reduce((v, file) => {
      v.hasOwnProperty(file.src.component) ? null : v[file.src.component] = { latest: '', versions: [] }
      v[file.src.component].versions.indexOf(file.src.version) === -1 ? v[file.src.component].versions.push(file.src.version) : null
      return v;
    }, {});

    // derive a default component from site startPage if possible
    const defaultComponent = playbook.site.startPage ? contentCatalog.resolvePage(playbook.site.startPage).src.origin.descriptor.name : Object.keys(componentVersions)[0] ;

    // check latest is not a prerelease and revert to latest actual release if it is
    for (const component of Object.keys(componentVersions)) {
      const latest = contentCatalog.getComponent(component).latest.version
      if (latest === '') {
        componentVersions[component].latest = '~'
        continue
      }
      const latestCheck = latest === ('current' || '') ? latest : semver.coerce(latest, { loose: true, includePrerelease: true })
      if (latestCheck && semver.prerelease(latestCheck)) {
        const releases = componentVersions[component].versions

        // turn releases into semver objects
        const semverList = []
        const semverObj = {}
        for (const r of releases) {
          const s = r === 'current' ? 'current' : semver.valid(semver.coerce(r, { loose: true, includePrerelease: true }))
          if (s) {
            semverList.push(s)
            semverObj[s] = r
          }
        }

        // ignore prereleases unless it's the only version
        for (s of semver.rsort(semverList)) {
          if (!semver.prerelease(s) || semverList.length === 1) {
            componentVersions[component].latest = semverObj[s]
            if (semverList.length !== 1) logger.info({  }, '%s version %s is the latest version according to semantic versioning rules', component, semverObj[s])
            break
          } else {
            logger.info({  }, '%s version %s is a prerelease', component, semverObj[s])
          }
        }

      } else {
        componentVersions[component].latest = latest
      }
    }

    const defaultSiteMapVersion = componentVersions[defaultComponent].latest

    const { sitemapVersion, data = { components: {}}, sitemapLocVersion = 'current' } = config

    if (!sitemapVersion && data.components.length == 0) {
      logger.error({  }, 'sitemap_version is required but has not been specified in the playbook. Default sitemap generation will be used')
      return
    }

    // check for each component if we can make a sitemap for the version specified
    for (const c of Object.keys(componentVersions)) {
      if (data.components[c]) logger.info({  }, '%s sitemap will be generated from version %s (specified by playbook data)', c, data.components[c])
      else if (sitemapVersion) logger.info({  }, '%s sitemap will be generated from version %s (specified by playbook)', c, sitemapVersion)
      else if (componentVersions[c].versions.length === 1) logger.info({  }, '%s sitemap will be generated from version %s because it is the only version available', c, componentVersions[c].latest)
      else if (componentVersions[c].latest) logger.info({  }, '%s sitemap will be generated from version %s (specified by semantic versioning rules)', c, componentVersions[c].latest)

      const versionToMap = data.components[c] || sitemapVersion || componentVersions[c].latest || defaultSiteMapVersion || ''
      if (versionToMap && versionToMap != '~' && !componentVersions[c].versions.includes(versionToMap)) {
        logger.warn({  }, 'Component \'%s\' does not include version \'%s\'. Available versions are \'%s\'', c, versionToMap, componentVersions[c].versions.join(', ') )
        unMappableComponents.push(c)
      }
    }

    const delegate = this.getFunctions().mapSite
    this.replaceFunctions({
      mapSite (playbook, pages) {
        const publishablePages = contentCatalog.getPages((page) => page.out)
        const mappablePages = publishablePages.reduce((mappable, file) => {

          // is this component mappable?
          // const mappableComponent = !unMappableComponents.includes(file.src.component)
          // what version of this file's component are we trying to add to the sitemap?
          let mappableVersion = data.components[file.src.component] || sitemapVersion || componentVersions[file.src.component].latest || defaultSiteMapVersion || ''
          if (mappableVersion === '~') mappableVersion = ''
          // is this file in that version of the component?
          const mappableFile = ( file.src.version == mappableVersion || ( !file.src.version && !mappableVersion ) )

          if (mappableFile) {
            logger.debug({ file: file.src }, 'Adding file in %s %s to sitemap', file.src.component, file.src.version || '(versionless)')
          } else {
            logger.debug({ file: file.src }, 'NOT adding file in %s %s to sitemap', file.src.component, file.src.version || '(versionlesscontent)')
          }

          mappedVersions[file.src.component] = ( typeof mappedVersions[file.src.component] != 'undefined' && mappedVersions[file.src.component] instanceof Array ) ? mappedVersions[file.src.component] : []

          if ( mappableVersion ) file.pub.url = file.pub.url.replace(mappableVersion,sitemapLocVersion)
          if ( mappableFile) {
            mappable.push(file);
            mappedComponentVersions[file.src.component] = mappableVersion;
          } else {
            if (!mappedVersions[file.src.component].includes(file.src.version)) mappedVersions[file.src.component].push(file.src.version)
          
          }
          return mappable;
        }, []);

        logger.info({  }, 'Adding %d %s to the %s', mappablePages.length, pluralize(mappablePages.length, 'page'), pluralize(mappedComponentVersions.length, 'sitemap'))
        return delegate.call(this, playbook, mappablePages)
      }
    })
  })
  .on('siteMapped', ({  }) => {

    const { siteCatalog } = this.getVariables()
    const { sitemapVersion, data = { components: componentVersions }, sitemapLocVersion = 'current', moveSitemapsToComponents = true } = config

    if(!moveSitemapsToComponents) {
      logger.info({  }, 'moveSitemapsToComponents has not been specified in the playbook. Sitemaps will be published to their default locations.')
      return
    }

    if (!sitemapVersion  && data.components.length == 0) {
      logger.error({  }, 'sitemap_version is required but has not been specified in the playbook. The default Antora sitemap generation will be used.')
      return
    }

    logger.info({  }, '%d %s generated', Object.keys(mappedComponentVersions).length, pluralize(Object.keys(mappedComponentVersions).length, 'Sitemap'))
  
    const siteFiles = siteCatalog.getFiles((page) => page.out)

    const sitemapFiles = siteFiles.reduce((sitemaps, file) => {
      if (file.out.path.startsWith(SITEMAP_STEM)) sitemaps.push(file)
      return sitemaps;
    }, []);

    sitemapFiles.forEach( (file) => {
      let dirname, versionDir, path_
      
      if (file.out.path.startsWith(SITEMAP_STEM) && sitemapFiles.length == 1) {
        dirname = Object.keys(mappedComponentVersions)[0]
        versionDir = mappedComponentVersions[dirname] != '' ? mappedComponentVersions[dirname] : '' ;
        path_ = path.join(dirname, versionDir, SITEMAP_STEM+SITEMAP_EXT)
      }

      if (file.out.path.replace(SITEMAP_STEM,'') == SITEMAP_EXT && sitemapFiles.length > 1) {
        logger.info({ file: file.out }, 'Paths updated in sitemap index file')
        stre = `${SITEMAP_PREFIX}(.*)${SITEMAP_EXT}`
        var re = new RegExp(stre, "g");
        file.contents = Buffer.from(file.contents.toString().replaceAll(re,`$1/${sitemapLocVersion}/${SITEMAP_STEM}${SITEMAP_EXT}`))
        siteCatalog.addFile(file)
      }

      if (file.out.path.startsWith(SITEMAP_PREFIX)) {
        dirname = file.out.path.replace(SITEMAP_PREFIX,'').replace(SITEMAP_EXT,'')
        versionDir = mappedComponentVersions[dirname] != '' ? mappedComponentVersions[dirname] : '' ;
        path_ = path.join(dirname, versionDir, SITEMAP_STEM+SITEMAP_EXT)  
      }

      if ( typeof path_ !== 'undefined' && path_ ) {
        logger.info({ file: file.out }, '%s has been moved to %s', file.out.path, path_)
        file.out.path = path_
        siteCatalog.addFile(file)
      }

    })

    // components without sitemaps
    for (const component in mappedVersions) {
      if (!Object.keys(mappedComponentVersions).includes(component)) {
        const mappableVersion = sitemapVersion || componentVersions[file.src.component].latest || defaultSiteMapVersion
        logger.warn({  }, 'Could not create sitemap for \'%s\' version \'%s\'. Available versions are \'%s\'', component, mappableVersion, componentVersions[component].versions.join(', ') )
      }
    }

    // components without sitemaps
    for (const component in data.components) {
      if (!Object.keys(mappedVersions).includes(component)) {
        logger.warn({  }, 'Sitemap generation for \'%s\' version \'%s\' specified, but no files for this component were found in the site catalog', component, data.components[component] )
      }
    }

  })
}
