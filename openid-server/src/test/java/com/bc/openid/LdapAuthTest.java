package com.bc.openid;

import org.junit.Before;
import org.junit.Test;

import java.util.HashMap;

/**
 * Relies on external resources.
 */
public class LdapAuthTest {

    private AuthenticationHandler auth;

    @Before
    public void setUp() throws Exception {
        auth = new LdapAuth();
        HashMap<String, String> parameters = new HashMap<>();
        parameters.put("com.bc.openid.authentication.param.host", "opec-portal-test");
        parameters.put("com.bc.openid.authentication.param.port", "389");
        auth.configure(parameters);
    }

    @Test
    public void testName() throws Exception {
        auth.authenticate("tstorm", "tstorm-ldap");
        // // todo - ts - continue here
    }
}