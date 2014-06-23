var actions = [];
var Action = function () {
};

var isAccessible = false;

actionManager.updateActions = function() {

    setActions();

    for (var i = 0; i < actions.length; i++) {
        var action = actions[i];
        var cssTarget = findCssTarget(action['jQueryCritera']);
        var allowedUserGroups = getAllowedUserGroups(action);
        setPermission(allowedUserGroups);
        $(cssTarget).attr('style', getStyleAttribute(cssTarget));
    }
};

function findCssTarget(jQueryCriteria) {
    var tag = jQueryCriteria['tag'];
    var attributes = jQueryCriteria['attributes'];
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
    return cssTarget;
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

function onRetrievePermissionsSuccess(data, opts) {
    isAccessible = data.is_accessible;
}

function onAjaxError(data, opt) {
    console.log('AJAX failed');
}

function getStyleAttribute(cssTarget) {
    var styleAttribute;
    var newStyle;
    if (isAccessible) {
        styleAttribute = $(cssTarget).attr('style');
        newStyle = styleAttribute.replace(/display:.*none/i, '');
    } else {
        styleAttribute = $(cssTarget).attr('style');
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

function setPermission(allowedUserGroups) {
    gisportal.genericSync('POST', gisportal.middlewarePath + '/permissions/' +

                                  allowedUserGroups, null, onRetrievePermissionsSuccess, onAjaxError, 'json', {});
}