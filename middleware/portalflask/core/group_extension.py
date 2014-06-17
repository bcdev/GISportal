from openid import extension

GROUPS_KEY = 'groups'

class GroupExtension(extension.Extension):
    ns_uri = 'http://openid.brockmann-consult.de/bcgroups'
    ns_alias = 'bcgroups'

    def getExtensionArgs(self):
        return {GROUPS_KEY: 'http://openid.brockmann-consult.de/bcgroups/groupNames'}


    def fromSuccessResponse(cls, success_response):
        self = cls()
        return success_response.extensionResponse(self.ns_uri, False)


    fromSuccessResponse = classmethod(fromSuccessResponse)