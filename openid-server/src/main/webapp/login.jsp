<!DOCTYPE html>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>OpenID-Provider Login</title>
</head>
<body>
<form name="openid-login-form" action="${destinationUrl}" method="post">
    <c:if test="${redirectionMessage != null}">
        ${redirectionMessage}
    </c:if>
    <table>
        <tr>
            <td>
                <input type="hidden" name="_loginAction" value="true"/>
            </td>
        </tr>
        <tr>
            <td>Username:</td>
            <td><input type="text" name="username"/>
            </td>
        </tr>
        <tr>
            <td>Password :</td>
            <td><input type="password" name="password"/>
            </td>
        </tr>
        <tr>
            <td align="center" colspan="2">
                <button type="submit">Login</button>
            </td>
        </tr>
    </table>
</form>
</body>
</html>