//Copyright (c) 2010, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id$

package gov.nasa.jpl.wrm.util;

//JDK imports
import java.sql.ResultSet;
import java.sql.SQLException;

//OODT imports
import gov.nasa.jpl.oodt.cas.filemgr.structs.Element;
import gov.nasa.jpl.oodt.cas.filemgr.structs.Product;
import gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType;
import gov.nasa.jpl.oodt.cas.metadata.Metadata;

/**
 * 
 * Builds File Manager Objects from WRM-relevant database schema fields.
 * 
 * @author mattmann
 * @version $Revision$
 * 
 */
public final class DatabaseStructFactory {

  public static Element toElement(ResultSet rs) throws SQLException {
    Element element = new Element();
    element.setElementId(rs.getString("parameter_id"));
    element.setElementName(rs.getString("shortName"));
    element.setDescription(rs.getString("description"));
    return element;
  }

  public static Product toProduct(ResultSet rs) throws SQLException {
    Product product = new Product();
    product.setProductId(rs.getString("granule_id"));
    product.setProductName(rs.getString("filename"));
    product.setProductStructure(Product.STRUCTURE_FLAT);
    product.setTransferStatus(Product.STATUS_RECEIVED);
    ProductType type = new ProductType();
    type.setProductTypeId(rs.getString("dataset_id"));
    product.setProductType(type);
    return product;
  }

  public static ProductType toProductType(ResultSet rs) throws SQLException {
    ProductType type = new ProductType();
    type.setProductTypeId(rs.getString("dataset_id"));
    type.setDescription(rs.getString("description"));
    type.setName(rs.getString("shortName"));
    type.setVersioner("gov.nasa.jpl.oodt.cas.filemgr.versioning.BasicVersioner"); // use basic versioner
    type.setProductRepositoryPath("file:///tmp"); // not moving files anyways

    Metadata typeMet = new Metadata();
    typeMet.addMetadata("DatasetId", type.getProductTypeId());
    typeMet.addMetadata("DatasetShortName", type.getName() != null ? type.getName():"");
    typeMet.addMetadata("DatasetLongName", rs.getString("longName") != null ? rs.getString("longName"):"");
    typeMet.addMetadata("Description", type.getDescription() != null ? type.getDescription():"");
    typeMet.addMetadata("Source", rs.getString("source") != null ? rs.getString("source"):"");
    typeMet.addMetadata("ReferenceURL", rs.getString("referenceURL") != null ? rs.getString("referenceURL"):"");
    type.setTypeMetadata(typeMet);
    return type;
  }

}
