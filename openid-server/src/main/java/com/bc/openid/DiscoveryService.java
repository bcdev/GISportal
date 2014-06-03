package com.bc.openid;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;

/**
 * Simple servlet with the only purpose to provide the XRDS document.
 *
 * Copied from https://gist.github.com/jdkanani/4303956,
 * turned into standard Java Servlet
 *
 * @author thomas
 *
 */
public class DiscoveryService extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        URI uri;
        try {
            uri = getClass().getResource("xrds.xml").toURI();
        } catch (URISyntaxException e) {
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            resp.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Cannot find resource 'xrds.xml'");
            return;
        }
        resp.setStatus(HttpServletResponse.SC_OK);
        File file = new File(uri);
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            while((line = reader.readLine()) != null) {
                line = line.replace("${endpointURI}", Config.getEndpointUrl());
                resp.getWriter().write(line);
            }
        }
    }

}