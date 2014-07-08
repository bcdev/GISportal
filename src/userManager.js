var actions = [];
var Action = function () {
};

gisportal.userManager.updateActions = function() {

    setActions();

    for (var i = 0; i < actions.length; i++) {
        var action = actions[i];
        var cssTargets = findCssTargets(action['jQueryCritera']);
        var allowedUserGroups = getAllowedUserGroups(action);
        var isAllowed = isUserAllowed(allowedUserGroups);
        cssTargets.forEach(function (element) {
            var cssTarget = element;
            $(cssTarget).attr('style', getStyleAttribute(isAllowed, cssTarget));
        });
    }
};

gisportal.userManager.isUserAllowedToView = function (userGroups) {
    return isUserAllowed(userGroups);
};

function findCssTargets(jQueryCriteria) {
    var cssTargets = [];
    jQueryCriteria.forEach(function (element) {
        var criterion = element;
        if ('id' in criterion) {
            var id = criterion['id'];
            var cssTarget = '#' + id;
        } else {
            var tag = criterion['tag'];
            var attributes = criterion['attributes'];
            var cssTarget = tag;
            cssTarget += '[';
            for (var key in attributes) {
                if (attributes.hasOwnProperty(key)) {
                    cssTarget += key + '=\'';
                    cssTarget += attributes[key] + '\'';
                    cssTarget += ' ';
                }
            }
            cssTarget += ']';
        }
        cssTargets.push(cssTarget);
    });
    return cssTargets;
}

function onRetrieveActionsSuccess(data, opt) {
    for (var i = 0; i < data.action_registry.length; i++) {
        var action = data.action_registry[i];
        var localAction = new Action();
        localAction.actionIdentifier = action.actionIdentifier;
        localAction.actionDescription = action.actionDescription;
        localAction.jQueryCritera = action.jQueryCriteria;
        localAction.allowedUserGroups = action.allowedUserGroups;
        actions.push(localAction)
    }
}

function onAjaxError(data, opt) {
    console.log('AJAX failed');
}

function getStyleAttribute(is_accessible, cssTarget) {
    var styleAttribute;
    var newStyle;
    if (is_accessible) {
        styleAttribute = $(cssTarget).attr('style');
        if (styleAttribute !== undefined) {
            newStyle = styleAttribute.replace(/display:.*none/i, '');
        }
    } else {
        styleAttribute = $(cssTarget).attr('style');
        if (styleAttribute === undefined) {
            return 'display:none';
        }
        if (styleAttribute.indexOf('display') == -1) {
            newStyle = styleAttribute + ';display:none';
        } else {
            newStyle = styleAttribute.replace(/display:.*/i, 'display:none');
        }
    }
    return newStyle;
}

function getAllowedUserGroups(action) {
    var allowedUserGroups = '';
    for (var j = 0; j < action['allowedUserGroups'].length; j++) {
        allowedUserGroups += action['allowedUserGroups'][j];
        if (j < action['allowedUserGroups'].length - 1) {
            allowedUserGroups += ',';
        }
    }
    return allowedUserGroups;
}

function setActions() {
    gisportal.genericSync('GET', gisportal.middlewarePath +
                                 '/retrieve_actions', null, onRetrieveActionsSuccess, onAjaxError, 'json', {});
}

function isUserAllowed(allowedUserGroups) {
    var localData;
    var onRetrievePermissionsSuccess = function(data, opts) {
        localData = data;
    };
    gisportal.genericSync('POST', gisportal.middlewarePath + '/permissions/' +
                                  allowedUserGroups, null, onRetrievePermissionsSuccess, onAjaxError, 'json', {});
    return localData.is_accessible;
}