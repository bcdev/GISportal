package com.bc.openid;

import org.openid4java.association.AssociationException;
import org.openid4java.message.AuthRequest;
import org.openid4java.message.AuthSuccess;
import org.openid4java.message.DirectError;
import org.openid4java.message.Message;
import org.openid4java.message.MessageException;
import org.openid4java.message.MessageExtension;
import org.openid4java.message.MessageExtensionFactory;
import org.openid4java.message.Parameter;
import org.openid4java.message.ParameterList;
import org.openid4java.message.ax.AxMessage;
import org.openid4java.message.ax.FetchRequest;
import org.openid4java.message.ax.FetchResponse;
import org.openid4java.message.sreg.SRegMessage;
import org.openid4java.message.sreg.SRegRequest;
import org.openid4java.message.sreg.SRegResponse;
import org.openid4java.server.ServerException;
import org.openid4java.server.ServerManager;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import javax.ws.rs.core.Response.Status;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * ProviderService - OpenID provider
 * NOTE: Some part of the code has been adopted from `OpenID4Java` library wiki.
 * <p>
 * Copied from https://gist.github.com/jdkanani/4303956,
 * turned into standard Java Servlet
 *
 * @author thomas
 */
public class AuthenticationService extends HttpServlet {

    private static final String SESSION_KEY_USER_MODEL = "userModel";
    private static final String SESSION_KEY_IS_AUTHENTICATED = "isAuthenticated";

    private static ServerManager manager = null;

    static {
        manager = new ServerManager();
        manager.setOPEndpointUrl(Config.getEndpointUrl());
        manager.getRealmVerifier().setEnforceRpId(false);
    }

    public AuthenticationService() {
        try {
            Message.addExtensionFactory(BcGroupsExtensionFactory.class);
        } catch (MessageException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            associateOrAuthenticate(req, resp);
        } catch (URISyntaxException | ServerException | AssociationException | MessageException e) {
            e.printStackTrace();
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            e.printStackTrace(resp.getWriter());
        }
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        doGet(req, resp);
    }

    private void associateOrAuthenticate(HttpServletRequest request, HttpServletResponse response)
            throws URISyntaxException, ServerException, AssociationException, MessageException, ServletException, IOException {

        Map<String, String> paramsMap = flattenParameters(request.getParameterMap());
        ParameterList parameterList = new ParameterList(paramsMap);

        boolean isLogOutAction = paramsMap.containsKey("_logoutAction");
        if (isLogOutAction) {
            HttpSession session = request.getSession();
            session.removeAttribute(SESSION_KEY_USER_MODEL);
            session.removeAttribute(SESSION_KEY_IS_AUTHENTICATED);
            redirectToLogin(request, response, "Successfully logged out.");
            return;
        }

        boolean isLoginAction = paramsMap.containsKey("_loginAction");
        if (isLoginAction) {
            String username = paramsMap.get("username");
            try {
                authenticate(username, paramsMap.get("password"), request);
                HttpSession session = request.getSession();
                paramsMap = (Map<String, String>) session.getAttribute("paramsMap");
                parameterList = new ParameterList(paramsMap);
            } catch (AuthenticationException e) {
                String redirectionMessage = "Error: " + e.getMessage();
                redirectToLogin(request, response, redirectionMessage);
                return;
            }
        }

        String mode = paramsMap.containsKey("openid.mode") ? paramsMap.get("openid.mode") : null;
        Message messageResponse;

        switch (mode) {
            case "associate":
                messageResponse = manager.associationResponse(parameterList);
                break;
            case "checkid_setup":
            case "checkid_immediate":

                // obtain user data needed to continue
                String userSelectedId = paramsMap.get("openid.identity");
                HttpSession session = request.getSession();
                Boolean isAuthenticated = Boolean.parseBoolean((String) session.getAttribute(SESSION_KEY_IS_AUTHENTICATED));
                if (!isAuthenticated) {
                    session.setAttribute("paramsMap", paramsMap);
                    redirectToLogin(request, response);
                    return;
                }

                String userSelectedClaimedId = parameterList.getParameterValue("openid.claimed_id");
                AuthRequest authReq = AuthRequest.createAuthRequest(parameterList, manager.getRealmVerifier());

                boolean signNow = false; // Sign after we added extensions.
                messageResponse = manager.authResponse(parameterList, userSelectedId, userSelectedClaimedId, true, signNow);

                if (messageResponse instanceof DirectError) {
                    response.setStatus(Status.INTERNAL_SERVER_ERROR.getStatusCode());
                    return;
                } else {
                    UserModel userModel = (UserModel) session.getAttribute(SESSION_KEY_USER_MODEL);

                    setEmail(authReq, userModel, messageResponse);
                    setUserGroups(authReq, userModel, messageResponse);

                    if (authReq.hasExtension(SRegMessage.OPENID_NS_SREG)) {
                        MessageExtension extensionRequestObject = authReq.getExtension(SRegMessage.OPENID_NS_SREG);
                        if (extensionRequestObject instanceof SRegRequest) {
                            Map<String, String> registrationData = new HashMap<>();
                            registrationData.put("fullname", userModel.getFullName());

                            SRegRequest sregReq = (SRegRequest) extensionRequestObject;
                            SRegResponse sregResp = SRegResponse.createSRegResponse(sregReq, registrationData);

                            messageResponse.addExtension(sregResp);
                        }
                    }

                    // Sign the auth success message.
                    manager.sign((AuthSuccess) messageResponse);

                    RequestDispatcher dispatcher = getServletContext().getRequestDispatcher("/consumer-redirection.jsp");
                    request.setAttribute("parameterMap", messageResponse.getParameterMap());
                    request.setAttribute("destinationUrl", messageResponse.getDestinationUrl(true));
                    request.setAttribute("logoutUrl", request.getRequestURL().toString());
                    dispatcher.forward(request, response);
                    return;
                }
            case "check_authentication":
                messageResponse = manager.verify(parameterList);
                break;
            default:
                response.setStatus(Status.BAD_REQUEST.getStatusCode());
                return;
        }
        // return the result to the user
        response.setStatus(Status.OK.getStatusCode());
        response.getWriter().write(messageResponse.keyValueFormEncoding());
    }

    static void setEmail(Message authReq, UserModel userModel, Message messageResponse) throws MessageException {
        if (authReq.hasExtension(AxMessage.OPENID_NS_AX)) {
            Map<String, String> axData = new HashMap<>();
            MessageExtension extensionRequestObject = authReq.getExtension(AxMessage.OPENID_NS_AX);
            if (extensionRequestObject instanceof FetchRequest) {
                FetchRequest fetchReq = (FetchRequest) extensionRequestObject;
                Map required = fetchReq.getAttributes(true);
                if (required != null && required.size() > 0) {
                    if (isAskingForMail(required)) {
                        axData.put("email", userModel.getEmailAddress());

                        FetchResponse fetchResp = FetchResponse.createFetchResponse(fetchReq, axData);
                        fetchResp.addAttribute("email", "http://schema.openid.net/contact/email", userModel.getEmailAddress());
                        messageResponse.addExtension(fetchResp);
                    }
                }
            }
        }
    }

    static void setUserGroups(Message authReq, UserModel userModel, Message messageResponse) throws MessageException {
        String namespace = BcGroupsExtensionFactory.TYPE_URI;
        GroupExtension extension = (GroupExtension) authReq.getExtension(namespace);
        String groupNames = Arrays.toString(userModel.getGroupNames()).replace(",", " ").replace("[", "").replace("]", "");
        extension.parameterList.set(new Parameter("groups", groupNames));
        messageResponse.addExtension(extension, "bcgroups");
    }

    private static boolean isAskingForMail(Map required) {
        for (Object value : required.values()) {
            if (value.toString().equals("http://schema.openid.net/contact/email") ||
                value.toString().equals("http://axschema.org/contact/email")) {
                return true;
            }
        }
        return required.containsKey("email");
    }

    private void authenticate(String username, String password, HttpServletRequest request) throws ServletException, IOException, AuthenticationException {
        AuthenticationHandler authenticationHandler = Config.getAuthenticationHandler();
        authenticationHandler.authenticate(username, password);
        HttpSession httpSession = request.getSession();
        UserModel userModel = authenticationHandler.getUserModel(username);
        httpSession.setAttribute(SESSION_KEY_USER_MODEL, userModel);
        httpSession.setAttribute(SESSION_KEY_IS_AUTHENTICATED, "true");
    }

    private void redirectToLogin(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        redirectToLogin(request, response, null);
    }

    private void redirectToLogin(HttpServletRequest request, HttpServletResponse response, String redirectionMessage) throws ServletException, IOException {
        RequestDispatcher dispatcher = getServletContext().getRequestDispatcher("/login.jsp");
        request.setAttribute("destinationUrl", Config.getEndpointUrl());
        request.setAttribute("redirectionMessage", redirectionMessage);
        dispatcher.forward(request, response);
    }

    private static Map<String, String> flattenParameters(Map parameters) {
        Map<String, String> map = new HashMap<>();
        for (Object key : parameters.keySet()) {
            String name = (String) key;
            String[] values = (String[]) parameters.get(name);
            if (values != null) {
                for (String value : values) {
                    map.put(name, value);
                }
                if (values.length > 1 && name.startsWith("openid.")) {
                    throw new IllegalArgumentException("Multiple parameters with the same name: " +
                                                       Arrays.toString(values));
                }
            }
        }
        return map;
    }

    public static class BcGroupsExtensionFactory implements MessageExtensionFactory {

        public static final String TYPE_URI = "http://openid.brockmann-consult.de/bcgroups";

        @Override
        public String getTypeUri() {
            return TYPE_URI;
        }

        @Override
        public MessageExtension getExtension(ParameterList parameterList, boolean isRequest) throws MessageException {
            return new GroupExtension(parameterList);
        }
    }

    public static class GroupExtension implements MessageExtension {

        private ParameterList parameterList;

        public GroupExtension(ParameterList parameterList) {
            this.parameterList = parameterList;
        }

        @Override
        public String getTypeUri() {
            return BcGroupsExtensionFactory.TYPE_URI;
        }

        @Override
        public ParameterList getParameters() {
            return parameterList;
        }

        @Override
        public void setParameters(ParameterList params) {
            this.parameterList = params;
        }

        @Override
        public boolean providesIdentifier() {
            return false;
        }

        @Override
        public boolean signRequired() {
            return false;
        }
    }
}