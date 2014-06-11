package com.bc.openid;

import org.junit.Before;
import org.junit.Test;

import java.util.Arrays;
import java.util.HashMap;

import static org.junit.Assert.*;

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
    public void testThomas() throws Exception {
        auth.authenticate("tstorm", "tstorm-ldap");
        UserModel userModel = auth.getUserModel("tstorm");
        assertNotNull(userModel);
        assertEquals("thomas.storm@brockmann-consult.de", userModel.getEmailAddress());
        assertEquals("Thomas Storm", userModel.getFullName());
        assertNull(userModel.getDateOfBirth());
        String[] groupNames = userModel.getGroupNames();
        Arrays.sort(groupNames);
        assertArrayEquals(new String[]{"admins", "cc_users"}, groupNames);
    }

    @Test
    public void testCoasti() throws Exception {
        auth.authenticate("ccolourinho", "cc-ldap");
        UserModel userModel = auth.getUserModel("ccolourinho");
        assertNotNull(userModel);
        assertEquals("cc@host.com", userModel.getEmailAddress());
        assertEquals("Coasti Colourinho", userModel.getFullName());
        assertNull(userModel.getDateOfBirth());
        assertArrayEquals(new String[] {"cc_users"}, userModel.getGroupNames());
    }
}