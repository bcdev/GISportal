package com.bc.openid;

import org.openid4java.association.AssociationException;
import org.openid4java.message.AuthRequest;
import org.openid4java.message.AuthSuccess;
import org.openid4java.message.DirectError;
import org.openid4java.message.Message;
import org.openid4java.message.MessageException;
import org.openid4java.message.MessageExtension;
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
 * <p/>
 * Copied from https://gist.github.com/jdkanani/4303956,
 * turned into standard Java Servlet
 *
 * @author thomas
 */
public class AuthenticationService extends HttpServlet {

    private static final String SESSION_KEY_USER_MODEL = "userModel";

    private static ServerManager manager = null;

    static {
        manager = new ServerManager();
        manager.setOPEndpointUrl(Config.getEndpointUrl());
        manager.getRealmVerifier().setEnforceRpId(false);
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            associateOrAuthenticate(req, resp);
        } catch (URISyntaxException | ServerException | AssociationException | MessageException e) {
            // todo -- add correct exception handling
            e.printStackTrace();
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

        boolean isLoginAction = paramsMap.containsKey("_loginAction");
        if (isLoginAction) {
            String loginIdentifier = paramsMap.get("identifier");
            boolean successfullyAuthenticated;
            try {
                authenticate(paramsMap.get("password"), loginIdentifier, request);
                successfullyAuthenticated = true;
            } catch (AuthenticationException e) {
                log("Unsuccessful authentication attempt by username '" + e.getUserName() + "'", e);
                successfullyAuthenticated = false;
            }
            if (successfullyAuthenticated) {
                HttpSession session = request.getSession();
                paramsMap = (Map<String, String>) session.getAttribute("paramsMap");
                parameterList = new ParameterList(paramsMap);
            } else {
                redirectToLogin(loginIdentifier, request, response);
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
                Boolean isAuthenticated = Boolean.parseBoolean((String) session.getAttribute("isAuthenticated"));
                if (!isAuthenticated) {
                    session.setAttribute("paramsMap", paramsMap);
                    redirectToLogin(userSelectedId, request, response);
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
                    UserModel registrationModel = (UserModel) session.getAttribute(SESSION_KEY_USER_MODEL);

                    setEmail(authReq, registrationModel, messageResponse);

                    if (authReq.hasExtension(SRegMessage.OPENID_NS_SREG)) {
                        MessageExtension extensionRequestObject = authReq.getExtension(SRegMessage.OPENID_NS_SREG);
                        if (extensionRequestObject instanceof SRegRequest) {
                            Map<String, String> registrationData = new HashMap<>();
                            registrationData.put("fullname", registrationModel.getFullName());
                            registrationData.put("dob", registrationModel.getDateOfBirth().toString());

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

    static void setEmail(Message authReq, UserModel registrationModel, Message messageResponse) throws MessageException {
        if (authReq.hasExtension(AxMessage.OPENID_NS_AX)) {
            Map<String, String> axData = new HashMap<>();
            MessageExtension extensionRequestObject = authReq.getExtension(AxMessage.OPENID_NS_AX);
            if (extensionRequestObject instanceof FetchRequest) {
                FetchRequest fetchReq = (FetchRequest) extensionRequestObject;
                Map required = fetchReq.getAttributes(true);
                if (required != null && required.size() > 0) {
                    if (isAskingForMail(required)) {
                        axData.put("email", registrationModel.getEmailAddress());

                        FetchResponse fetchResp = FetchResponse.createFetchResponse(fetchReq, axData);
                        fetchResp.addAttribute("email", "http://schema.openid.net/contact/email", registrationModel.getEmailAddress());
                        messageResponse.addExtension(fetchResp);
                    }
                }
            }
        }
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

    private void authenticate(String password, String identifier, HttpServletRequest request) throws ServletException, IOException, AuthenticationException {
        AuthenticationHandler authenticationHandler = Config.getAuthenticationHandler();
        authenticationHandler.authenticate(identifier, password);
        HttpSession httpSession = request.getSession();
        UserModel userModel = authenticationHandler.getUserModel(identifier);
        httpSession.setAttribute(SESSION_KEY_USER_MODEL, userModel);
        httpSession.setAttribute("isAuthenticated", "true");
    }

    private void redirectToLogin(String identifier, HttpServletRequest httpRequest, HttpServletResponse httpResponse) throws ServletException, IOException {
        RequestDispatcher dispatcher = getServletContext().getRequestDispatcher("/login.jsp");
        httpRequest.setAttribute("identifier", identifier);
        httpRequest.setAttribute("destinationUrl", Config.getEndpointUrl());
        dispatcher.forward(httpRequest, httpResponse);
    }

    private static Map<String, String> flattenParameters(Map parameters) {
        Map<String, String> map = new HashMap<>();
        for (Object key : parameters.keySet()) {
            String name = (String)key;
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

}