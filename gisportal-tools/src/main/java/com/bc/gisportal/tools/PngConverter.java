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

package com.bc.gisportal.tools;

import com.bc.ceres.core.ProgressMonitor;
import org.esa.beam.dataio.netcdf.DefaultNetCdfWriter;
import org.esa.beam.dataio.netcdf.metadata.profiles.cf.CfNetCdf4WriterPlugIn;
import org.esa.beam.dataio.netcdf.nc.NFileWriteable;
import org.esa.beam.dataio.netcdf.nc.NVariable;
import org.esa.beam.framework.dataio.ProductIO;
import org.esa.beam.framework.datamodel.Band;
import org.esa.beam.framework.datamodel.Product;
import org.esa.beam.framework.datamodel.ProductData;
import org.esa.beam.util.io.FileUtils;
import ucar.ma2.DataType;

import java.io.File;
import java.io.IOException;

/**
 * Simple main for converting png-images into NetCDF.
 *
 * @author thomas
 */
public class PngConverter {

    public static void main(String[] args) throws IOException, NoSuchFieldException, IllegalAccessException {

        if (args.length != 1) {
            System.out.println("Exactly one argument expected");
            printUsageAndQuit();
        } else if (!(new File(args[0]).exists())) {
            System.out.println("Path does not exist");
            printUsageAndQuit();
        } else if (!new File(args[0]).isFile()) {
            System.out.println("Path must point to a file, not a directory");
            printUsageAndQuit();
        }

        File png = new File(args[0]);
        Product product = ProductIO.readProduct(png);

        Band red = product.getBand("red");
        Band green = product.getBand("green");
        Band blue = product.getBand("blue");
        Band gray = product.getBand("gray");
        Band alpha = product.getBand("alpha");

        if (red == null || green == null || blue == null || gray == null || alpha == null) {
            System.out.println("Invalid product: '" + png + "'");
            product.dispose();
            png.delete();
            System.exit(101);
        }

        String targetFilename = png.getParent() + File.separator + FileUtils.getFilenameWithoutExtension(png) + "_waqss_archive.nc";

        product.getBandGroup().remove(red);
        product.getBandGroup().remove(green);
        product.getBandGroup().remove(blue);
        product.getBandGroup().remove(alpha);

        DefaultNetCdfWriter writer = new DefaultNetCdfWriter(new CfNetCdf4WriterPlugIn() {
            @Override
            public NFileWriteable createWritable(String outputPath) throws IOException {
                NFileWriteable writable = super.createWritable(outputPath);
                NVariable crs = writable.addScalarVariable("crs", DataType.INT);
                crs.addAttribute("wkt", "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.01745329251994328,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]]");
                return writable;
            }
        });

        writer.writeProductNodes(product, targetFilename);
        product.addBand(red);
        product.addBand(green);
        product.addBand(blue);

        for (int y = 0; y < product.getSceneRasterHeight(); y++) {
            ProductData.Float rasterData = new ProductData.Float(product.getSceneRasterWidth());
            gray.readRasterData(0, y, product.getSceneRasterWidth(), 1, rasterData, ProgressMonitor.NULL);
            writer.writeBandRasterData(gray, 0, y, product.getSceneRasterWidth(), 1, rasterData, ProgressMonitor.NULL);
        }

        writer.close();
        product.dispose();
        if (!png.delete()) {
            System.out.println("WARNING: unable to delete file '" + png + "'");
        }
    }

    private static void printUsageAndQuit() {
        System.out.println("Usage:");
        System.out.println("        PngConverter <path_to_file>");
        System.exit(-1);
    }
}
