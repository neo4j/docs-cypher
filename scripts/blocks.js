function deprecated() {
    var self = this
    self.named('DEPRECATED')
    self.onContexts(['example', 'paragraph','open'])
    self.process(function(parent, reader, context, attrs) {
        var lines = reader.getLines()
        var blockType = context['cloaked-context'] == 'paragraph' ? 'admonition' : context['cloaked-context'];
        // console.log(context)
        return self.createBlock(parent, 'admonition', lines, { 'name': 'deprecated', 'caption': 'deprecated'})

    })
}

// NB - should role be changed to name in the other extensions listed here? 
// use of name comes from https://github.com/asciidoctor/asciidoctor-extensions-lab/issues/9

function console() {
    var self = this
    self.named('console')
    self.onContext('listing')
    self.process(function () {
        return
    })
}

function queryResult() {
    var self = this
    self.named('queryresult')
    self.onContext('listing')
    self.process(function(parent, reader) {
        var lines = reader.getLines()
        return self.createBlock(parent, 'listing', lines, { 'role': 'queryresult' })

    })
}

function vis() {
    var self = this
    self.named('vis')
    self.onContext('listing')
    self.process(function(parent, reader) {
        var lines = reader.getLines()
        return self.createBlock(parent, 'listing', lines, { 'role': 'vis' })

    })
}

function register(registry, context) {
    registry.block(':DEPRECATED', deprecated)
    registry.block('listing:console', console)
    registry.block('listing:queryresult', queryResult)
    registry.block('listing:vis', vis)
}

module.exports.register = register