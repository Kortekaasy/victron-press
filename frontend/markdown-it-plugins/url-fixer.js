'use strict';

module.exports = function url_fixer(md, options) {
    options = options || {};
    options = {
        baseUrl: options.baseUrl || null,
    };

    function fixUrl(url, token, env) {
        const baseUrl = env.baseUrl || options.baseUrl;

        // TODO:
        // - change url's from md to html if rendered
        // - change url's to correct language version, controlled by option
        // - change relative url's to absolute for pdf
        // - force victron url's to https
        // - ...?
        return url;
    }

    md.core.ruler.push('url-fixer', function(state) {
        let hasFixed = false;
        for (let i = 0; i < state.tokens.length; i++) {
            const blockToken = state.tokens[i];
            if (blockToken.type === 'inline' && blockToken.children) {
                for (let j = 0; j < blockToken.children.length; j++) {
                    const token = blockToken.children[j];
                    if (token.attrs) {
                        for (let k = 0; k < token.attrs.length; k++) {
                            const attr = token.attrs[k];
                            if (attr[0] == 'href' || attr[0] == 'src') {
                                const oldUrl = attr[1];
                                const newUrl = fixUrl(oldUrl, token, state.env);
                                if (newUrl !== oldUrl) {
                                    attr[1] = newUrl;
                                    hasFixed = true;
                                }
                            }
                        }
                    }
                }
            }
        }
        return hasFixed;
    });
};