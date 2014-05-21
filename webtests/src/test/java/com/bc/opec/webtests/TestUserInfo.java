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

package com.bc.opec.webtests;

import org.junit.Before;
import org.junit.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.interactions.Actions;

import static org.junit.Assert.*;

/**
 * @author thomas
 */
public class TestUserInfo {

    private WebDriver driver;

    @Before
    public void setUp() throws Exception {
        final WebTestBase webTestBase = WebTestBase.getInstance();
        driver = webTestBase.getDriver();
        webTestBase.closePopups();
    }

    @Test
    public void testThatUserInfoBalloonIsShown() throws Exception {
        WebElement webElement = driver.findElement(By.xpath("//*/div[@aria-describedby='user-info-balloon']"));
        assertNotNull(webElement);
        if (webElement.getAttribute("aria-describedby").equals("user-info-balloon")) {
            assertEquals("none", webElement.getCssValue("display").toLowerCase());

            final WebElement element = driver.findElement(By.id("userInfoToggleBtn"));
            Actions actions = new Actions(driver);
            actions.moveToElement(element).click().perform();

            assertEquals("block", webElement.getCssValue("display").toLowerCase());
        }
    }

}
