const assumptions = {
    setPublicClassFields: true
}

const plugins = [
    ['@babel/plugin-proposal-decorators', { decoratorsBeforeExport: true }],
    ['@babel/plugin-proposal-class-properties']
]

module.exports = { assumptions, plugins }
