module.exports = function (registry) {
  registry.preprocessor(function () {
    var self = this
    self.process(function (doc, reader) {
      var lines = reader.lines
      var header = false
      var pageRoles = []
      var pattern = /\[(role="?|\.)(.+)\]/
      for (var i = lines.length - 1; i > 0; i--) {
        if (!header) {
          const found = lines[i].match(pattern);
          if (found) {
            pageRoles.push(found[2].replaceAll('.',' ').replaceAll('"',''))
          }
          if (lines[i].match(/= \w*/)) {
            header = true
          }
        }
      }
      if (pageRoles.length > 0) {
        doc.setAttribute('page-role', pageRoles.join(' '))
      } 
      return reader
    })
  })
}
