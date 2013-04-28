//Copyright (c) 2010, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id$

package org.apache.climate.repository;

//JDK imports
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.sql.DataSource;

import org.apache.climate.util.DatabaseStructFactory;

//OODT imports
import gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager;
import gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType;
import gov.nasa.jpl.oodt.cas.filemgr.structs.exceptions.RepositoryManagerException;

/**
 * 
 * Leverages the information in the {@link WRMCatalog}'s dataset table to list
 * out {@link ProductType}s.
 * 
 * @author mattmann
 * @version $Revision$
 * 
 */
public class WRMRepositoryManager implements RepositoryManager {

  private static final Logger LOG = Logger.getLogger(WRMRepositoryManager.class.getName());
  
  private DataSource dataSource;

  public WRMRepositoryManager(DataSource dataSource) {
    this.dataSource = dataSource;
  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager#addProductType
   * (gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType)
   */
  public void addProductType(ProductType productType)
      throws RepositoryManagerException {
    String sql = "INSERT INTO dataset (longName, shortName, description) VALUES ('"
        + productType.getName()
        + "', '"
        + productType.getName()
        + "', '"
        + productType.getDescription() + "'";
    Connection conn = null;
    Statement statement = null;

    try {
      conn = this.dataSource.getConnection();
      statement = conn.createStatement();
      statement.execute(sql);
    } catch (SQLException e) {
      e.printStackTrace();
    } finally {
      if (statement != null) {
        try {
          statement.close();
        } catch (Exception ignore) {
        }
        statement = null;
      }

      if (conn != null) {
        try {
          conn.close();
        } catch (Exception ignore) {
        }
        conn = null;
      }

    }

  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager#getProductTypeById
   * (java.lang.String)
   */
  public ProductType getProductTypeById(String productTypeId)
      throws RepositoryManagerException {
    String sql = "SELECT dataset_id, shortName, longName, source, referenceURL, description from dataset WHERE dataset_id = "
        + productTypeId;
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;
    ProductType productType = null;

    try {
      conn = this.dataSource.getConnection();
      statement = conn.createStatement();
      LOG.log(Level.FINE, "Executing: ["+sql+"]");
      rs = statement.executeQuery(sql);
      while (rs.next()) {
        productType = DatabaseStructFactory.toProductType(rs);
      }
    } catch (SQLException e) {
      e.printStackTrace();
    } finally {
      if (rs != null) {
        try {
          rs.close();
        } catch (Exception ignore) {
        }
        rs = null;
      }

      if (statement != null) {
        try {
          statement.close();
        } catch (Exception ignore) {
        }
        statement = null;
      }

      if (conn != null) {
        try {
          conn.close();
        } catch (Exception ignore) {
        }
        conn = null;
      }

    }

    return productType;
  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager#getProductTypeByName
   * (java.lang.String)
   */
  public ProductType getProductTypeByName(String productTypeName)
      throws RepositoryManagerException {
    String sql = "SELECT dataset_id, shortName, longName, source, referenceURL, description from dataset WHERE shortName = '"
        + productTypeName + "'";
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;
    ProductType productType = null;

    try {
      conn = this.dataSource.getConnection();
      statement = conn.createStatement();
      rs = statement.executeQuery(sql);
      while (rs.next()) {
        productType = DatabaseStructFactory.toProductType(rs);
      }
    } catch (SQLException e) {
      e.printStackTrace();
    } finally {
      if (rs != null) {
        try {
          rs.close();
        } catch (Exception ignore) {
        }
        rs = null;
      }

      if (statement != null) {
        try {
          statement.close();
        } catch (Exception ignore) {
        }
        statement = null;
      }

      if (conn != null) {
        try {
          conn.close();
        } catch (Exception ignore) {
        }
        conn = null;
      }

    }

    return productType;
  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager#getProductTypes
   * ()
   */
  public List<ProductType> getProductTypes() throws RepositoryManagerException {
    String sql = "SELECT dataset_id, shortName, longName, source, referenceURL, description from dataset ORDER BY dataset_id DESC";
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;
    List<ProductType> productTypes = new Vector<ProductType>();

    try {
      conn = this.dataSource.getConnection();
      statement = conn.createStatement();
      rs = statement.executeQuery(sql);
      while (rs.next()) {
        productTypes.add(DatabaseStructFactory.toProductType(rs));
      }
    } catch (SQLException e) {
      e.printStackTrace();
    } finally {
      if (rs != null) {
        try {
          rs.close();
        } catch (Exception ignore) {
        }
        rs = null;
      }

      if (statement != null) {
        try {
          statement.close();
        } catch (Exception ignore) {
        }
        statement = null;
      }

      if (conn != null) {
        try {
          conn.close();
        } catch (Exception ignore) {
        }
        conn = null;
      }
    }

    return productTypes;

  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager#modifyProductType
   * (gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType)
   */
  public void modifyProductType(ProductType productType)
      throws RepositoryManagerException {
    String sql = "UPDATE dataset SET shortName='" + productType.getName()
        + "',description='" + productType.getDescription()
        + "' WHERE dataset_id = " + productType.getProductTypeId();

    Connection conn = null;
    Statement statement = null;

    try {
      conn = this.dataSource.getConnection();
      statement = conn.createStatement();
      statement.execute(sql);
    } catch (SQLException e) {
      e.printStackTrace();
    } finally {
      if (statement != null) {
        try {
          statement.close();
        } catch (Exception ignore) {
        }
        statement = null;
      }

      if (conn != null) {
        try {
          conn.close();
        } catch (Exception ignore) {
        }
        conn = null;
      }

    }

  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.repository.RepositoryManager#removeProductType
   * (gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType)
   */
  public void removeProductType(ProductType productType)
      throws RepositoryManagerException {
    String sql = "DELETE FROM dataset WHERE dataset_id = "
        + productType.getProductTypeId();

    Connection conn = null;
    Statement statement = null;

    try {
      conn = this.dataSource.getConnection();
      statement = conn.createStatement();
      statement.execute(sql);
    } catch (SQLException e) {
      e.printStackTrace();
    } finally {
      if (statement != null) {
        try {
          statement.close();
        } catch (Exception ignore) {
        }
        statement = null;
      }

      if (conn != null) {
        try {
          conn.close();
        } catch (Exception ignore) {
        }
        conn = null;
      }

    }

  }

}
