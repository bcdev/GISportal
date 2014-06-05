/*
 * Copyright (C) 2011 Brockmann Consult GmbH (info@brockmann-consult.de)
 * 
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version.
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, see http://www.gnu.org/licenses/
 */

package com.bc.openid;

import java.util.HashMap;
import java.util.Map;

/**
 * Responsible for authenticating the user and providing information about him.
 *
 * @author thomas
 */
public abstract class AuthenticationHandler {

    private Map<String, Boolean> authInformation = new HashMap<>();

    protected AuthenticationHandler() {
        // necessary for instantiation via reflection
    }

    /**
     * Try to authenticate the user.
     *
     * @param username The user's username.
     * @param password The user's password.
     *
     * @return <code>true</code> if user can be logged in with the given credentials.
     */
    public final boolean authenticate(String username, String password) {
        boolean authenticated = authenticateImpl(username, password);
        authInformation.put(username, authenticated);
        return authenticated;
    }

    /**
     * Gets the user model for the given username. User <b>must</b> be authenticated before calling this method.
     *
     * @param username The user's username.
     *
     * @return The user model for the given username.
     *
     * @throws java.lang.IllegalStateException if this method is called for an unauthenticated user.
     */
    public final UserModel getUserModel(String username) {
        if (!isAuthenticated(username)) {
            throw new IllegalStateException(
                    "Trying to fetch user information about non-logged in user '" + username + "'.");
        }
        return getUserModelImpl(username);
    }

    protected abstract boolean authenticateImpl(String username, String password);

    protected abstract UserModel getUserModelImpl(String username);

    public void configure(Map<String, String> parameters) {

    }

    private boolean isAuthenticated(String username) {
        return authInformation.containsKey(username) && authInformation.get(username);
    }
}
