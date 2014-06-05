package com.bc.openid;

import org.junit.Test;
import org.openid4java.message.AuthRequest;
import org.openid4java.message.AuthSuccess;
import org.openid4java.message.Message;
import org.openid4java.message.Parameter;
import org.openid4java.message.ParameterList;
import org.openid4java.message.ax.FetchRequest;

import static org.junit.Assert.*;

public class AuthenticationServiceTest {

    private static final String EXPECTED_MAIL_ADDRESS = "muuuh@miau.com";

    @Test
    public void testSetEmail() throws Exception {
        final UserModel registrationModel = new UserModel();
        registrationModel.setEmailAddress(EXPECTED_MAIL_ADDRESS);

        final ParameterList authParams = new ParameterList();
        authParams.set(new Parameter("openid.mode", "checkid_setup"));
        authParams.set(new Parameter("required", "true"));
        Message authRequest = AuthRequest.createMessage(authParams);

        final ParameterList fetchParams = new ParameterList();
        fetchParams.set(new Parameter("required", "true"));
        fetchParams.set(new Parameter("mode", "fetch_request"));
        fetchParams.set(new Parameter("type.true", ""));
        final FetchRequest fetchRequest = FetchRequest.createFetchRequest(fetchParams);
        fetchRequest.addAttribute("ext0", "http://schema.openid.net/contact/email", true);
        fetchRequest.addAttribute("ext1", "http://axschema.org/contact/email", true);
        authRequest.addExtension(fetchRequest);

        Message messageResponse = AuthSuccess.createMessage();

        // execution
        AuthenticationService.setEmail(authRequest, registrationModel, messageResponse);

        // verification
        assertTrue(!messageResponse.getExtensions().isEmpty());
        assertEquals(EXPECTED_MAIL_ADDRESS, messageResponse.getParameterValue("openid.ext1.value.email"));
    }
}