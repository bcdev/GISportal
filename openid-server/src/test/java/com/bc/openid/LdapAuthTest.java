package com.bc.openid;

import org.junit.Before;
import org.junit.Test;

import javax.naming.directory.Attributes;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
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
        parameters.put("com.bc.openid.authentication.host", "opec-portal-test");
        parameters.put("com.bc.openid.authentication.port", "389");
        parameters.put("com.bc.openid.authentication.ldap.path", "dc=opec,dc=bc,dc=com");
        parameters.put("com.bc.openid.authentication.ldap.user-ou", "users");
        parameters.put("com.bc.openid.authentication.ldap.group-ou", "groups");
        auth.configure(parameters);
    }

    @Test
    public void testName() throws Exception {
        // Create initial context
        DirContext ctx = new InitialDirContext();

// Read supportedSASLMechanisms from root DSE
        Attributes attrs = ctx.getAttributes("ldap://auth.bc.local:389");
        System.out.println("LdapAuthTest.testName");
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