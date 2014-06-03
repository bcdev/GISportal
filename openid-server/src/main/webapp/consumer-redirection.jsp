<!DOCTYPE html>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<html>
<head>
    <title>OpenID Consumer Redirection</title>
</head>
<body onload="document.forms['openid-consumer-redirection'].submit();">
<form name="openid-consumer-redirection" action="${destinationUrl}" method="post">
    <c:forEach var="parameter" items="${parameterMap}">
        <input type="hidden" name="${parameter.key}" value="${parameter.value}"/>
    </c:forEach>
    <button type="submit">Continue</button>
</form>
</body>
</html>