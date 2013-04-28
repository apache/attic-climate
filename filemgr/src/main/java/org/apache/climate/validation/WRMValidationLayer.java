//Copyright (c) 2010, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id$

package org.apache.climate.validation;

//JDK imports
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Vector;

import javax.sql.DataSource;

import org.apache.climate.util.DatabaseStructFactory;

//OODT imports
import gov.nasa.jpl.oodt.cas.filemgr.structs.Element;
import gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType;
import gov.nasa.jpl.oodt.cas.filemgr.structs.exceptions.ValidationLayerException;
import gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer;

/**
 * 
 * Determines the mapping of {@Element}s to {@link ProductType}s by
 * reading the WRM catalog schema tables concerning parameters and datasets.
 * 
 * @author mattmann
 * @version $Revision$
 * 
 */
public class WRMValidationLayer implements ValidationLayer {

  private DataSource ds;

  public WRMValidationLayer(DataSource ds) {
    this.ds = ds;
  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#addElement(gov
   * .nasa.jpl.oodt.cas.filemgr.structs.Element)
   */
  public void addElement(Element element) throws ValidationLayerException {
    String sql = "INSERT INTO parameter (dataset_id, longName, shortName, description) "
        + "VALUES (-1, '"
        + element.getElementName()
        + "','"
        + element.getElementName() + "', '" + element.getDescription() + "')";
    Connection conn = null;
    Statement statement = null;

    try {
      conn = ds.getConnection();
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
   * @seegov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#
   * addElementToProductType(gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType,
   * gov.nasa.jpl.oodt.cas.filemgr.structs.Element)
   */
  public void addElementToProductType(ProductType productType, Element element)
      throws ValidationLayerException {
    String sql = "INSERT INTO dpMap (dataset_id, parameter_id) VALUES ("
        + productType.getProductTypeId() + ", " + element.getElementId() + ")";
    Connection conn = null;
    Statement statement = null;

    try {
      conn = ds.getConnection();
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
   * gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#getElementById
   * (java.lang.String)
   */
  public Element getElementById(String elementId)
      throws ValidationLayerException {
    String sql = "SELECT parameter_id, shortName, description from parameter WHERE parameter_id = "
        + elementId;
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;
    Element element = null;

    try {
      conn = ds.getConnection();
      statement = conn.createStatement();
      rs = statement.executeQuery(sql);
      while (rs.next()) {
        element = DatabaseStructFactory.toElement(rs);
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

    return element;
  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#getElementByName
   * (java.lang.String)
   */
  public Element getElementByName(String elementName)
      throws ValidationLayerException {
    String sql = "SELECT parameter_id, shortName, description from parameter WHERE shortName = '"
        + elementName + "'";
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;
    Element element = null;

    try {
      conn = ds.getConnection();
      statement = conn.createStatement();
      rs = statement.executeQuery(sql);
      while (rs.next()) {
        element = DatabaseStructFactory.toElement(rs);
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

    return element;
  }

  /*
   * (non-Javadoc)
   * 
   * @see gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#getElements()
   */
  public List<Element> getElements() throws ValidationLayerException {
    String sql = "SELECT parameter_id, shortName, description from parameter ORDER by parameter_id DESC";
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;
    List<Element> elements = new Vector<Element>();

    try {
      conn = ds.getConnection();
      statement = conn.createStatement();
      rs = statement.executeQuery(sql);
      while (rs.next()) {
        elements.add(DatabaseStructFactory.toElement(rs));
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

    return elements;
  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#getElements(gov
   * .nasa.jpl.oodt.cas.filemgr.structs.ProductType)
   */
  public List<Element> getElements(ProductType productType) {
    String sql = "SELECT parameter_id, shortName, description from parameter WHERE dataset_id = "
        + productType.getProductTypeId() + " ORDER by parameter_id DESC";
    Connection conn = null;
    Statement statement = null;
    ResultSet rs = null;
    List<Element> elements = new Vector<Element>();

    try {
      conn = ds.getConnection();
      statement = conn.createStatement();
      rs = statement.executeQuery(sql);
      while (rs.next()) {
        elements.add(DatabaseStructFactory.toElement(rs));
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

    return elements;
  }

  /*
   * (non-Javadoc)
   * 
   * @see
   * gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#modifyElement(
   * gov.nasa.jpl.oodt.cas.filemgr.structs.Element)
   */
  public void modifyElement(Element element) throws ValidationLayerException {
    String sql = "UPDATE parameter SET longName='" + element.getElementName()
        + "', shortName='" + element.getElementName() + "',description='"
        + element.getDescription() + "' WHERE parameter_id = "
        + element.getElementId();

    Connection conn = null;
    Statement statement = null;

    try {
      conn = ds.getConnection();
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
   * gov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#removeElement(
   * gov.nasa.jpl.oodt.cas.filemgr.structs.Element)
   */
  public void removeElement(Element element) throws ValidationLayerException {
    String sql = "DELETE FROM parameter WHERE parameter_id = "
        + element.getElementId();

    Connection conn = null;
    Statement statement = null;

    try {
      conn = ds.getConnection();
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
   * @seegov.nasa.jpl.oodt.cas.filemgr.validation.ValidationLayer#
   * removeElementFromProductType
   * (gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType,
   * gov.nasa.jpl.oodt.cas.filemgr.structs.Element)
   */
  public void removeElementFromProductType(ProductType productType,
      Element element) throws ValidationLayerException {
    String sql = "DELETE FROM dpMap WHERE parameter_id = "
        + element.getElementId() + " and dataset_id = "
        + productType.getProductTypeId();

    Connection conn = null;
    Statement statement = null;

    try {
      conn = ds.getConnection();
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
