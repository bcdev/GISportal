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

import javax.naming.Context;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.directory.Attribute;
import javax.naming.directory.SearchControls;
import javax.naming.directory.SearchResult;
import javax.naming.ldap.Control;
import javax.naming.ldap.InitialLdapContext;
import java.util.Hashtable;
import java.util.Map;

/**
 * LDAP implementation of the {@link com.bc.openid.AuthenticationHandler} interface.
 *
 * @author thomas
 */
public class LdapAuth extends AuthenticationHandler {

    private static final String DEFAULT_PORT = "389";
    private static final String KEY_HOST = "com.bc.openid.authentication.param.host";
    private static final String KEY_PORT = "com.bc.openid.authentication.param.port";

    private String host;
    private String port;

    private UserModel userModel;


    @Override
    protected void authenticateImpl(String username, String password) throws AuthenticationException {
        Hashtable<String, String> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, ldapUrl(host, port) + "/ou=users,dc=opec,dc=bc,dc=com");
        env.put(Context.SECURITY_AUTHENTICATION, "simple");

        try (MyInitialLdapContext context = new MyInitialLdapContext(env)) {
            SearchControls searchControls = new SearchControls();
            NamingEnumeration<SearchResult> results = context.search("", "(uid=" + username + ")", searchControls);
            SearchResult searchResult = null;
            if(results.hasMoreElements()) {
                searchResult = results.nextElement();
                if(results.hasMoreElements()) {
                    throw new AuthenticationException(username, "Matched multiple users for username: '" + username + "'");
                }
            }
            setUserModel(searchResult);
        } catch (NamingException e) {
            throw new AuthenticationException(username, e);
        }
    }

    private void setUserModel(SearchResult searchResult) throws NamingException {
        NamingEnumeration<String> iDs = searchResult.getAttributes().getIDs();
        while (iDs.hasMore()) {
            Attribute attribute = searchResult.getAttributes().get(iDs.next());
            System.out.println("LdapAuth.setUserModel");
//        userModel.setEmailAddress();
        }
    }

    @Override
    protected UserModel getUserModelImpl(String username) {
        return userModel;
    }

    @Override
    public void configure(Map<String, String> parameters) {
        host = parameters.get(KEY_HOST);
        String port = parameters.get(KEY_PORT);
        if (port == null || port.equals("")) {
            port = DEFAULT_PORT;
        }
        this.port = port;
    }

    private static String ldapUrl(String host, String port) {
        return "ldap://" + host + ":" + port;
    }

    private static class MyInitialLdapContext extends InitialLdapContext implements AutoCloseable {

        public MyInitialLdapContext(Hashtable<String, String> env) throws NamingException {
            super(env, new Control[0]);
        }
    }



    // this allows logging in, too
    // but I had difficulties retrieving the user data

    /*

        LdapLoginModule loginModule = new LdapLoginModule();
        HashSet<Principal> principals = new HashSet<>();
        Subject subject = new Subject(false, principals, new HashSet<>(), new HashSet<>());
        HashMap<String, Object> options = new HashMap<>();
        options.put("userProvider", ldapUrl(host, port) + "/ou=users,dc=opec,dc=bc,dc=com");
        options.put("userFilter", "(uid=" + username + ")");
        options.put("useSSL", "false");
        options.put("debug", "true");
        loginModule.initialize(subject, callbacks -> {
            for (Callback callback : callbacks) {
                if (callback instanceof NameCallback) {
                    ((NameCallback)callback).setName(username);
                } else if (callback instanceof PasswordCallback) {
                    ((PasswordCallback)callback).setPassword(password.toCharArray());
                }
            }
        }, null, options);

        try {
            loginModule.login();
            loginModule.commit();
        } catch (LoginException e) {
            throw new AuthenticationException(username, e);
        }
     */
}
