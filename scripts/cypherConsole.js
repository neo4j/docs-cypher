module.exports = function (registry) {
  registry.treeProcessor(function () {
    var self = this
    self.process(function(doc) {
      doc.findBy({ 'context': 'pass' })
        .forEach(block => {
          if (block.lines[0] == '<formalpara role="cypherconsole">') {
            block.lines = []
          }
        })
    })
  })
}
