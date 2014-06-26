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
import javax.naming.directory.Attributes;
import javax.naming.directory.SearchControls;
import javax.naming.directory.SearchResult;
import javax.naming.ldap.Control;
import javax.naming.ldap.InitialLdapContext;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;

/**
 * LDAP implementation of the {@link com.bc.openid.AuthenticationHandler} interface.
 *
 * @author thomas
 */
public class LdapAuth extends AuthenticationHandler {

    private static final String DEFAULT_PORT = "389";
    private static final String KEY_HOST = "com.bc.openid.authentication.host";
    private static final String KEY_PORT = "com.bc.openid.authentication.port";
    private static final String KEY_LDAP_PATH = "com.bc.openid.authentication.ldap.path";
    private static final String KEY_LDAP_USER_OU = "com.bc.openid.authentication.ldap.user-ou";
    private static final String KEY_LDAP_GROUP_OU = "com.bc.openid.authentication.ldap.group-ou";

    private String host;
    private String port;

    private UserModel userModel;
    private String ldapPath;
    private String userOu;
    private String groupOu;


    @Override
    protected void authenticateImpl(String username, String password) throws AuthenticationException {
        getLogger().apply("authenticating user " + username);
        Hashtable<String, String> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, ldapUrl(host, port));
        env.put(Context.SECURITY_AUTHENTICATION, "simple");

        try (MyInitialLdapContext context = new MyInitialLdapContext(env)) {
            SearchResult userEntry = getUserEntry(username, context);
            setUserModel(username, userEntry);

            try {
                checkUsernameAndPassword(password, userEntry);
            } catch (NamingException e) {
                e.printStackTrace();
                getLogger().apply("Wrong combination of username and password. Reason: " + e.getMessage());
                throw new AuthenticationException(username, "Wrong combination of username and password", e);
            }

            Object uidNumber = userEntry.getAttributes().get("uidNumber").get(0);
            List<String> groupNames = getGroupNames(context, uidNumber);
            userModel.setGroupNames(groupNames.toArray(new String[groupNames.size()]));
        } catch (NamingException e) {
            throw new AuthenticationException(username, e);
        }
    }

    private void checkUsernameAndPassword(String password, SearchResult userEntry) throws NamingException {
        Hashtable<String, Object> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, ldapUrl(host, port));
//        env.put(Context.SECURITY_AUTHENTICATION, "simple");
        env.put(Context.SECURITY_AUTHENTICATION, "DIGEST-MD5"); // todo - make configurable
        env.put(Context.SECURITY_CREDENTIALS, password);
        String dn = "cn=" + userEntry.getAttributes().get("cn").get(0).toString() + ",ou=users," + ldapPath;
        env.put("com.sun.jndi.ldap.trace.ber", System.err);
//        env.put(Context.SECURITY_PRINCIPAL, dn);
        env.put(Context.SECURITY_PRINCIPAL, "thomas");
        new InitialLdapContext(env, new Control[0]);
    }

    private List<String> getGroupNames(MyInitialLdapContext context, Object uidNumber) throws NamingException, AuthenticationException {
        SearchControls groupSearch = new SearchControls();
        groupSearch.setSearchScope(SearchControls.SUBTREE_SCOPE);
        NamingEnumeration groups = context.search("ou=" + groupOu + "," + ldapPath, "(objectClass=posixGroup)", groupSearch);

        List<String> groupNames = new ArrayList<>();

        while (groups.hasMore()) {
            SearchResult group = (SearchResult) groups.next();
            Attributes groupAttributes = group.getAttributes();
            String groupName = groupAttributes.get("cn").get(0).toString();
            Attribute memberUids = groupAttributes.get("memberUid");
            for (int i = 0; i < memberUids.size(); i++) {
                if (memberUids.get(i).equals(uidNumber)) {
                    groupNames.add(groupName);
                }
            }
        }
        return groupNames;
    }

    private SearchResult getUserEntry(String username, MyInitialLdapContext context) throws NamingException, AuthenticationException {
        SearchControls searchControls = new SearchControls();
        searchControls.setReturningAttributes(new String [] {"givenName", "sn", "mail", "cn", "uidNumber"});
        String filter = "(uid=" + username + ")";

        NamingEnumeration<SearchResult> results = context.search("ou=" + userOu + "," + ldapPath, filter, searchControls);
        SearchResult userEntry;
        if (results.hasMoreElements()) {
            userEntry = results.nextElement();
            if (results.hasMoreElements()) {
                throw new AuthenticationException(username, "Matched multiple users for username: '" + username + "'");
            }
        } else {
            throw new AuthenticationException(username, "Wrong combination of username and password");
        }
        return userEntry;
    }

    private void setUserModel(String username, SearchResult userEntry) throws NamingException {
        userModel = new UserModel();
        Attribute mailAttribute = userEntry.getAttributes().get("mail");
        if (mailAttribute != null) {
            userModel.setEmailAddress(mailAttribute.get().toString());
        }
        String fullName = "";
        Attribute givenNameAttribute = userEntry.getAttributes().get("givenName");
        Attribute surnameAttribute = userEntry.getAttributes().get("sn");
        if (givenNameAttribute != null) {
            fullName += givenNameAttribute.get().toString();
        }
        if (surnameAttribute != null) {
            fullName += givenNameAttribute != null ? " " : "";
            fullName += surnameAttribute.get().toString();
        }
        userModel.setFullName(fullName);
        userModel.setUsername(username);
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

        if (!parameters.containsKey(KEY_LDAP_PATH)) {
            throw new IllegalArgumentException("Mandatory key '" + KEY_LDAP_PATH + "' missing in config.");
        }
        ldapPath = parameters.get(KEY_LDAP_PATH);

        if (!parameters.containsKey(KEY_LDAP_USER_OU)) {
            throw new IllegalArgumentException("Mandatory key '" + KEY_LDAP_USER_OU + "' missing in config.");
        }
        userOu = parameters.get(KEY_LDAP_USER_OU);

        if (!parameters.containsKey(KEY_LDAP_GROUP_OU)) {
            throw new IllegalArgumentException("Mandatory key '" + KEY_LDAP_GROUP_OU + "' missing in config.");
        }
        groupOu = parameters.get(KEY_LDAP_GROUP_OU);



    }

    private static String ldapUrl(String host, String port) {
        return "ldap://" + host + ":" + port;
    }

    private static class MyInitialLdapContext extends InitialLdapContext implements AutoCloseable {

        public MyInitialLdapContext(Hashtable<String, String> env) throws NamingException {
            super(env, new Control[0]);
        }
    }
}
