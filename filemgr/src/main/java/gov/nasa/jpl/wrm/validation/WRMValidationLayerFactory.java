//Copyright (c) 2010, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id$

package gov.nasa.jpl.wrm.validation;

//JDK imports
import javax.sql.DataSource;

//OODT imports
import gov.nasa.jpl.oodt.cas.commons.database.DatabaseConnectionBuilder;
import gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer;
import gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayerFactory;
import gov.nasa.jpl.oodt.cas.metadata.util.PathUtils;

/**
 * 
 * Constructs new {@link WRMValidationLayer}s.
 * 
 * @author mattmann
 * @version $Revision$
 * 
 */
public class WRMValidationLayerFactory implements ValidationLayerFactory {

  private DataSource dataSource;

  public WRMValidationLayerFactory() {
    String jdbcUrl = null, user = null, pass = null, driver = null;

    jdbcUrl = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.validation.jdbc.url"));
    user = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.validation.jdbc.user"));
    pass = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.validation.jdbc.pass"));
    driver = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.validation.jdbc.driver"));

    this.dataSource = DatabaseConnectionBuilder.buildDataSource(user, pass,
        driver, jdbcUrl);
  }

  /*
   * (non-Javadoc)
   * 
   * @seegov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayerFactory#
   * createValidationLayer()
   */
  public ValidationLayer createValidationLayer() {
    return new WRMValidationLayer(this.dataSource);
  }

}
