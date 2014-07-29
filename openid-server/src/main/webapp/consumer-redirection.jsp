<!DOCTYPE html>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<html>
<head>
    <title>OpenID Consumer Redirection</title>
    <link rel="stylesheet" type="text/css" href="<%=request.getContextPath()%>/style.css">
</head>
<body>
<form name="openid-consumer-redirection" action="${destinationUrl}" method="post">
    <c:forEach var="parameter" items="${parameterMap}">
        <input type="hidden" name="${parameter.key}" value="${parameter.value}"/>
    </c:forEach>
    <button type="submit">Continue</button>
</form>

&nbsp;

<form name="openid-consumer-logout" action="${logoutUrl}" method="post">
    <c:forEach var="parameter" items="${parameterMap}">
        <input type="hidden" name="${parameter.key}" value="${parameter.value}"/>
    </c:forEach>
    <input type="hidden" name="_logoutAction" value="true"/>
    <button type="submit">Log out</button>
</form>

<jsp:include page="footer.jsp"/>

</body>
</html>