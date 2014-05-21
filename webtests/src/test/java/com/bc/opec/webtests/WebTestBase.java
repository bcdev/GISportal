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

import org.junit.Assert;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

import static org.junit.Assert.*;

/**
 * Base test class for web tests. Requirements:
 *
 * <ul>
 *     <li>Google Chrome browser must be installed</li>
 *     <li>Environment variable <i>webdriver.chrome.driver</i> must be set to chromedriver executable</li>
 *     <li>Environment variable <i>webtest.portal.url</i> must be set to URL of portal</li>
 * </ul>
 *
 * @author thomas
 */
public final class WebTestBase {

    private WebDriver driver;

    private WebTestBase() {
        setChromeDriverLocation();
        String url = getUrl();

        driver = new ChromeDriver();
        driver.navigate().to(url);
    }

    private static void setChromeDriverLocation() {
        String chromeDriverLocation = System.getenv("webdriver.chrome.driver");
        if (chromeDriverLocation == null) {
            fail("Need to set environment variable 'webdriver.chrome.driver'");
        }
        System.setProperty("webdriver.chrome.driver", chromeDriverLocation);
    }

    private static String getUrl() {
        String url = System.getenv("webtest.portal.url");
        if (url == null) {
            fail("Need to set environment variable 'webtest.portal.url'");
        }
        if (!url.startsWith("http://")) {
            url = "http://" + url;
        }
        return url;
    }

    private static class Holder {

        private static final WebTestBase INSTANCE = new WebTestBase();

        private Holder() {
        }
    }

    public static WebTestBase getInstance() {
        return Holder.INSTANCE;
    }

    public WebDriver getDriver() {
        return driver;
    }

    public void closePopups() {
        Assert.assertTrue(driver.getTitle().startsWith("OPEC"));
        for (WebElement e : driver.findElements(By.tagName("Button"))) {
            if (e.getAttribute("title").equals("Close")) {
                e.click();
                break;
            }
        }
        for (WebElement e : driver.findElements(By.tagName("Button"))) {
            if (e.getText().equals("No")) {
                e.click();
                break;
            }
        }
        driver.findElement(By.xpath("//*/div[@aria-describedby='gisportal-layerSelection']/div/div/button[@title='close']")).click();
    }

    @Override
    protected void finalize() throws Throwable {
        System.clearProperty("webdriver.chrome.driver");
        driver.close();
        driver.quit();
        super.finalize();
    }

}
