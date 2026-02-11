/*
Inline macro: label

<name>:<target>[<attr>]

Macro behavior

<name>

  Is the macro name, `label`.
  It can only contain letters, digits or dash characters and cannot start with a dash.

<target>

  Mandatory, cannot contain white space characters.
  Should only be lowercase characters, e.g. label:deprecated[].
  The target name format should be like: example-target-css-class, e.g. label:example-target-css-class[].
  This will be the CSS class.
  If no text in the <attr> is specified the name of the target will be used (in a formatted form, see the code).

<attr>

  A list of attributes enclosed in square brackets.
  The list items are seperated by comma `,`.
  The first item in the list will be used as the text if it is specified, e.g. label:deprecated[Deprecated 4.3].
  Keep the text minimal length.
  The text will be HTML escaped for some characters.
    & is replaced with &amp;
    < is replaced with &lt;
    > is replaced with &gt;
  If comma is needed in the text use `"` enclosure, e.g. label:warning["Unsuported 4.1, 4.2, and 4.3"].
  The `]` character inside attribute lists must be escaped with a backslash.

Examples:

  label:deprecated[]
  label:deprecated[Deprecated In 4.4]
  label:deprecated["Using commas, example"]

Sources:

  https://docs.asciidoctor.org/asciidoctor.js/latest/extend/extensions/inline-macro-processor/
*/

const renameLabels = {
    'apoc-core': 'APOC Core',
    'apoc-full': 'APOC Full',
    'na': 'N / A',
    'warning': 'Warning!',
    'danger': 'Danger!',
    'mac-os': 'Mac OS',
    'cluster-member-core': 'CORE',
    'cluster-member-read-replica': 'READ_REPLICA',
    'cluster-member-single': 'SINGLE',
    'not-on-aura': 'Not Available on Aura',
    'aura-db-enterprise': 'AuraDB Virtual Dedicated Cloud',
    'aura-db-vdc': 'AuraDB Virtual Dedicated Cloud',
}

module.exports.register = function(registry, context) {
    registry.inlineMacro('label', function () {
        const self = this

        self.process(function(parent, target, attr) {
            let text

            try {
                let attributes = attr.$positional
                if (attributes) {
                  text = attributes[0]
                }
            } catch (error) {}

            if (text === undefined) {
                text = renameLabels[ target ]
            }

            if (text === undefined ) {
                text = target.split(/\s|-/)
                .map(text => text.substr(0, 1).toUpperCase() + text.substr(1))
                .join(' ')
            }

            const label = `<span class="label label--${target}">${text}</span>`
            return self.createInline(parent, 'quoted', label)
        })
    })
}
