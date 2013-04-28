//Copyright (c) 2010, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id$

package org.apache.climate.repository;

//JDK imports
import javax.sql.DataSource;

//OODT imports
import gov.nasa.jpl.oodt.cas.commons.database.DatabaseConnectionBuilder;
import gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager;
import gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManagerFactory;
import gov.nasa.jpl.oodt.cas.metadata.util.PathUtils;

/**
 * 
 * Constructs new {@link WRMRepositoryManager}s.
 * 
 * @author mattmann
 * @version $Revision$
 * 
 */
public class WRMRepositoryManagerFactory implements RepositoryManagerFactory {

  private DataSource dataSource;

  public WRMRepositoryManagerFactory() {
    String jdbcUrl = null, user = null, pass = null, driver = null;

    jdbcUrl = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.repositorymgr.jdbc.url"));
    user = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.repositorymgr.jdbc.user"));
    pass = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.repositorymgr.jdbc.pass"));
    driver = PathUtils.replaceEnvVariables(System
        .getProperty("gov.nasa.jpl.wrm.repositorymgr.jdbc.driver"));

    this.dataSource = DatabaseConnectionBuilder.buildDataSource(user, pass,
        driver, jdbcUrl);
  }

  /*
   * (non-Javadoc)
   * 
   * @seegov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManagerFactory#
   * createRepositoryManager()
   */
  public RepositoryManager createRepositoryManager() {
    return new WRMRepositoryManager(this.dataSource);
  }

}
