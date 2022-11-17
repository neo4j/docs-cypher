const kroki = require('asciidoctor-kroki')

function dot() {
    var self = this
    self.named('dot')
    self.onContext('listing')
    self.process(function (parent, reader, attrs, context) {
        var text = reader.$read()
        if (!text.includes("digraph")) {
            text = "[graphviz]\n----\ndigraph L { node [shape=record style=rounded];\n" + text + "\n}\n----"
        } else {
            text = "[graphviz]\n----\n" + text + "\n----"
        }
        self.parseContent(parent, text)
    })
}

function register (registry, context) {
    registry.block('listing:dot',dot)
}

module.exports.register = register