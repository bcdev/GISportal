package com.bc.openid;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
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
        URI uri = null;
        try {
            uri = getClass().getResource("xrds.xml").toURI();
        } catch (URISyntaxException e) {
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            return;
        }
        resp.setStatus(HttpServletResponse.SC_OK);
        final File file = new File(uri);
        final char[] buffer = new char[1024];
        try (FileReader reader = new FileReader(file)) {
            while (reader.read(buffer) != -1) {
                resp.getWriter().write(buffer);
            }

        }
    }

}