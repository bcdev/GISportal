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
        assertEquals("tstorm", userModel.getUsername());
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
        assertEquals("ccolourinho", userModel.getUsername());
        assertArrayEquals(new String[] {"cc_users"}, userModel.getGroupNames());
    }

    @Test
    public void testWrongPassword() throws Exception {
        try {
            auth.authenticate("tstorm", "kaputt");
            fail();
        } catch (AuthenticationException expected) {
            assertEquals("Wrong combination of username and password", expected.getMessage());
        }
    }

    @Test
    public void testNotExistingUser() throws Exception {
        try {
            auth.authenticate("Godot", "any");
            fail();
        } catch (AuthenticationException expected) {
            assertEquals("Wrong combination of username and password", expected.getMessage());
        }
    }
}