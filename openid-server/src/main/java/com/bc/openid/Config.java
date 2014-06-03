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

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * @author thomas
 */
class Config {

    private static Properties properties;
    private static final String PROPERTY_KEY_ENDPOINTURI = "com.bc.openid.endpointuri";

    static {
        try (InputStream propertyStream = Config.class.getResourceAsStream("openid.properties")) {
            properties = new Properties();
            properties.load(propertyStream);
        } catch (IOException e) {
            throw new IllegalStateException("Cannot load properties file", e);
        }
    }

    static String getEndpointUrl() {
        return properties.getProperty(PROPERTY_KEY_ENDPOINTURI);
    }

}
