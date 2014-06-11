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

import java.time.Instant;

/**
 * Default implementation; authenticates always if default password is given.
 *
 * @author thomas
 */
public class AuthenticateAll extends AuthenticationHandler {

    @Override
    protected void authenticateImpl(String username, String password) throws AuthenticationException {
        if (username == null) {
            throw new AuthenticationException(null, "Username must not be null");
        }
        boolean authenticated = password != null && password.equalsIgnoreCase("miau");
        if (!authenticated) {
            throw new AuthenticationException(username);
        }
    }

    @Override
    protected UserModel getUserModelImpl(String username) {
        UserModel userModel = new UserModel();
        userModel.setDateOfBirth(Instant.parse("1952-11-03T00:00:00.00Z"));
        userModel.setEmailAddress("jamesbond@mi6.com");
        userModel.setFullName("James Bond");
        userModel.setOpenId(username);
        return userModel;
    }

}