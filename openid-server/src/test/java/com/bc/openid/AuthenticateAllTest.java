package com.bc.openid;

import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

public class AuthenticateAllTest {

    private AuthenticationHandler authenticateAll;

    @Before
    public void setUp() throws Exception {
        authenticateAll = new AuthenticateAll();
    }

    @Test
    public void testAuthenticateSuccess_1() throws Exception {
        try {
            authenticateAll.authenticate("anything", "anything");
        } catch (AuthenticationException e) {
            fail(e.getMessage());
        }
    }

    @Test
    public void testAuthenticateFails_1() throws Exception {
        try {
            authenticateAll.authenticate(null, "anything");
            fail();
        } catch (AuthenticationException expected) {
            assertNull(expected.getUserName());
            assertTrue(expected.getMessage().equals("Username must not be null"));
        }
    }

    @Test
    public void testGetUserModel() throws Exception {
        try {
            authenticateAll.getUserModel("schnabbelewoppski");
            fail();
        } catch (IllegalStateException ignored) {
            // ok
        }

        authenticateAll.authenticate("schnabbelewoppski", "anything");
        UserModel userModel = authenticateAll.getUserModel("schnabbelewoppski");
        assertNotNull(userModel);

    }
}