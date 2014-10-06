<!DOCTYPE html>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>OpenID-Provider Login</title>
    <link rel="stylesheet" type="text/css" href="/openid<%=request.getContextPath()%>/style.css">
</head>
<body>
<form name="openid-login-form" action="${destinationUrl}" method="post">
    <c:if test="${redirectionMessage != null}">
        <div class="text subtext" style="color: #C8142F">${redirectionMessage}</div>
        <p>&nbsp;</p>
    </c:if>

<%@ page import="java.util.Enumeration" %>
    <%@ page import="java.util.HashMap" %>
    <%@ page import="java.util.Map" %>
    <%
        Map<String, String> allParameters = new HashMap<String, String>();
        Enumeration a = request.getParameterNames();
        while (a.hasMoreElements()) {
            String paramName = a.nextElement().toString();
            allParameters.put(paramName, request.getParameter(paramName));
        }
        pageContext.setAttribute("itemList", allParameters);
    %>

    <span class="text">Log in with your BC credentials.</span><br/>
    <span class="text subtext">Hint: use the credentials you are also using for the BC Calvalus service.</span>

    <c:forEach var="entry" items="${itemList}">
        <input type="hidden" name="${entry.key}" value="${entry.value}"/>
    </c:forEach>

    <table class="table">
        <tr>
            <td>
                <input type="hidden" name="_loginAction" value="true"/>
            </td>
        </tr>
        <tr>
            <td><span class="text subtext">Username:</span></td>
            <td><input type="text" name="username"/>
            </td>
        </tr>
        <tr>
            <td><span class="text subtext">Password :</span></td>
            <td><input type="password" name="password"/>
            </td>
        </tr>
        <tr>
            <td class="buttonCell" colspan="2">
                <button class="button" type="submit">Login</button>
            </td>
        </tr>
    </table>

    <jsp:include page="footer.jsp"/>

</form>
</body>
</html>