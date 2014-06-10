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
            authenticateAll.authenticate("anything", "miau");
        } catch (AuthenticationException e) {
            fail(e.getMessage());
        }
    }

    @Test
    public void testAuthenticateFails_1() throws Exception {
        try {
            authenticateAll.authenticate(null, "miau");
            fail();
        } catch (AuthenticationException expected) {
            assertNull(expected.getUserName());
            assertTrue(expected.getMessage().equals("Username must not be null"));
        }
    }

    @Test
    public void testAuthenticateFails_2() throws Exception {
        try {
            authenticateAll.authenticate("anything", "wuff");
            fail();
        } catch (AuthenticationException expected) {
            assertTrue(expected.getUserName().equals("anything"));
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

        authenticateAll.authenticate("schnabbelewoppski", "miau");
        UserModel userModel = authenticateAll.getUserModel("schnabbelewoppski");
        assertNotNull(userModel);

    }
}