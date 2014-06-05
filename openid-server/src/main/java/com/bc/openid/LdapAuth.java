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

import java.util.Map;

/**
 * LDAP implementation of the {@link com.bc.openid.AuthenticationHandler} interface.
 *
 * @author thomas
 */
public class LdapAuth extends AuthenticationHandler {

    private String host;
    private String port;

    @Override
    protected boolean authenticateImpl(String username, String password) {
        return false;
    }

    @Override
    protected UserModel getUserModelImpl(String username) {
        return new UserModel();
    }

    @Override
    public void configure(Map<String, String> parameters) {
        host = parameters.get("com.bc.openid.authentication.param.host");
        port = parameters.get("com.bc.openid.authentication.param.port");
    }
}
