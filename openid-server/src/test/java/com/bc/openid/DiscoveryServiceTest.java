package com.bc.openid;

import org.junit.Test;

import javax.servlet.http.HttpServletResponse;
import java.io.PrintWriter;
import java.io.StringWriter;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

public class DiscoveryServiceTest {

    @Test
    public void testDoGet() throws Exception {

        DiscoveryService discoveryService = new DiscoveryService();
        HttpServletResponse response = mock(HttpServletResponse.class);
        StringWriter writer = new StringWriter();
        when(response.getWriter()).thenReturn(new PrintWriter(writer));

        String result = writer.toString();
        assertEquals("", result);

        discoveryService.doGet(null, response);
        result = writer.toString();

        assertTrue(result.startsWith("<?xml version"));
        assertTrue(result.matches("[\\s\\S]*\\<URI\\>.+\\</URI\\>[\\s\\S]*"));
        assertFalse(result.contains("<URI>${endpointURI}</URI>"));

    }
}