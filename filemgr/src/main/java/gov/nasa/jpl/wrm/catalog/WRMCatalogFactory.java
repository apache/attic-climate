//Copyright (c) 2010, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id$

package gov.nasa.jpl.wrm.catalog;

import javax.sql.DataSource;

import gov.nasa.jpl.oodt.cas.commons.database.DatabaseConnectionBuilder;
import gov.nasa.jpl.oodt.cas.filemgr.catalog.Catalog;
import gov.nasa.jpl.oodt.cas.filemgr.catalog.CatalogFactory;
import gov.nasa.jpl.oodt.cas.metadata.util.PathUtils;
import gov.nasa.jpl.wrm.validation.WRMValidationLayerFactory;

/**
 * WRMCatalogFactory
 * 
 * Implements the CatalogFactory interface to provide a factory for WRMCatalog.
 * The properties referenced in this class can be edited in the
 * filemgr.properties file in [filemgr_home]/etc/filemgr.properties
 * 
 * @author ahart, cgoodale
 * 
 */
public class WRMCatalogFactory implements CatalogFactory {

    // The data source
    protected DataSource dataSource = null;
    
    // The page size
    protected int pageSize;

    public WRMCatalogFactory() {

        String jdbcUrl = null, user = null, pass = null, driver = null;

        jdbcUrl = PathUtils.replaceEnvVariables(System
                .getProperty("gov.nasa.jpl.wrm.catalog.datasource.jdbc.url"));
        user = PathUtils.replaceEnvVariables(System
                .getProperty("gov.nasa.jpl.wrm.catalog.datasource.jdbc.user"));
        pass = PathUtils.replaceEnvVariables(System
                .getProperty("gov.nasa.jpl.wrm.catalog.datasource.jdbc.pass"));
        driver = PathUtils
                .replaceEnvVariables(System
                        .getProperty("gov.nasa.jpl.wrm.catalog.datasource.jdbc.driver"));
        

        dataSource = DatabaseConnectionBuilder.buildDataSource(user, pass,
                driver, jdbcUrl);
        pageSize = Integer.valueOf(PathUtils.replaceEnvVariables(System
            .getProperty("gov.nasa.jpl.wrm.catalog.datasource.pageSize")));

    }

    public Catalog createCatalog() {
        return new WRMCatalog(dataSource, new WRMValidationLayerFactory().createValidationLayer(), pageSize);
    }

}
