//Copyright (c) 2009, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id: MetadataResource.java 7160 2009-11-17 15:52:16Z pramirez $

package gov.nasa.jpl.oodt.cas.curation.service;

//OODT imports
import gov.nasa.jpl.oodt.cas.curation.structs.ExtractorConfig;
import gov.nasa.jpl.oodt.cas.curation.util.CurationXmlStructFactory;
import gov.nasa.jpl.oodt.cas.curation.util.ExtractorConfigReader;
import gov.nasa.jpl.oodt.cas.filemgr.catalog.Catalog;
import gov.nasa.jpl.oodt.cas.filemgr.repository.XMLRepositoryManager;
import gov.nasa.jpl.oodt.cas.filemgr.structs.Product;
import gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType;
import gov.nasa.jpl.oodt.cas.filemgr.structs.Reference;
import gov.nasa.jpl.oodt.cas.filemgr.structs.exceptions.CatalogException;
import gov.nasa.jpl.oodt.cas.filemgr.structs.exceptions.RepositoryManagerException;
import gov.nasa.jpl.oodt.cas.filemgr.util.GenericFileManagerObjectFactory;
import gov.nasa.jpl.oodt.cas.metadata.MetExtractor;
import gov.nasa.jpl.oodt.cas.metadata.Metadata;
import gov.nasa.jpl.oodt.cas.metadata.SerializableMetadata;
import gov.nasa.jpl.oodt.cas.metadata.exceptions.MetExtractionException;
import gov.nasa.jpl.oodt.cas.metadata.util.GenericMetadataObjectFactory;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.Iterator;

import javax.servlet.ServletContext;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import javax.ws.rs.DefaultValue;
import javax.ws.rs.FormParam;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MultivaluedMap;
import javax.ws.rs.core.UriInfo;
import javax.ws.rs.Consumes;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;
import net.sf.json.JSONSerializer;

@Path("metadata")
/**
 * 
 * A web-service endpoint for dealing with CAS {@link Metadata} object.
 * 
 * @author pramirez
 * @version $Id: MetadataResource.java 7160 2009-11-17 15:52:16Z pramirez $
 */
public class MetadataResource extends CurationService {
  
  @Context
  UriInfo uriInfo;

  private static final long serialVersionUID = 1930946924218765724L;

  public static final String STAGING = "staging";

  public static final String CATALOG = "catalog";

  public static final String PRODUCT_TYPE = "productType";
  
  public MetadataResource(){
    
  }

  public MetadataResource(@Context ServletContext context) {

  }

  @GET
  @Path(STAGING)
  @Produces("text/plain")
  public String getStagingMetadata(@QueryParam("id") String id,
      @DefaultValue(FORMAT_HTML) @QueryParam("format") String format,
      @QueryParam("configId") String configId,
      @DefaultValue("false") @QueryParam("overwrite") Boolean overwrite,
      @Context HttpServletRequest req, @Context HttpServletResponse res) {
    
      // this.sendRedirect("login.jsp", uriInfo, res);

      Metadata metadata = null;
      
      try {
        metadata = this.getStagingMetadata(id, configId, overwrite);
      } catch (Exception e) {
        return "<div class=\"error\">" + e.getMessage() + "</div>";
      }
      
      if (FORMAT_HTML.equals(format)) {
        return this.getMetadataAsHTML(metadata);
      }
      return this.getMetadataAsJSON(metadata).toString();
  }
  
  @GET
  @Path("extractor/config")
  @Produces("text/plain")
  public String getMetExtractorConfigList(
      @DefaultValue("") @QueryParam("current") String current,
      @DefaultValue(FORMAT_HTML) @QueryParam("format") String format) {
    String[] configIds = this.getFilesInDirectory(this.config
        .getMetExtrConfUploadPath(), false);

    if (FORMAT_HTML.equals(format)) {
      return this.getExtractorConfigIdsAsHTML(configIds, current);
    }
    return this.getExtractorConfigIdsAsJSON(configIds);
  }

  protected String getExtractorConfigIdsAsHTML(String[] configIds,
      String current) {
    StringBuffer html = new StringBuffer();
    for (int i = 0; i < configIds.length; i++) {
      html.append("<option ");
      if (configIds[i].equals(current)) {
        html.append("selected ");
      }
      html.append("value=\"");
      html.append(configIds[i]);
      html.append("\">");
      html.append(configIds[i]);
      html.append("</option>\r\n");
    }
    return html.toString();
  }
  
  protected String getExtractorConfigIdsAsJSON(String[] configIds) {
    // TODO: Support JSON
    return "Not Implemented...";
  }

  /**
   * 
   * @param id
   *          Relative path from staging root to product. The met extension will
   *          be added to this id to look up and see if a met file exists with
   *          in the met area.
   * @param configId
   *          Reference to the extractor config. {@link ExtractorConfigReader}
   *          will load the configuration
   * @param overwrite
   *          Flag to indicate whether or not to overwrite a met file if present
   *          in the staging area.
   * @return The {@link Metadata} retrieved from the met area path if present or
   *         extracted using the met extractor config.
   * @throws FileNotFoundException
   * @throws InstantiationException
   * @throws IOException
   * @throws MetExtractionException
   */
  protected Metadata getStagingMetadata(String id, String configId,
      Boolean overwrite) throws FileNotFoundException, InstantiationException,
      IOException, MetExtractionException {
    if (configId == null || configId.trim().length() == 0) {
      return this.readMetFile(id + CurationService.config.getMetExtension());
    } else {
      String relMetPath = id.startsWith("/") ? id : "/" + id;
      String pathToMetFile = CurationService.config.getMetAreaPath()
          + relMetPath + CurationService.config.getMetExtension();
      if (!overwrite && new File(pathToMetFile).exists()) {
        return this.readMetFile(id + CurationService.config.getMetExtension());
      } else {
        // Make sure the parent directory exists
        new File(pathToMetFile).getParentFile().mkdirs();
        Metadata metadata = this.runMetExtractor(id, ExtractorConfigReader
            .readFromDirectory(
                new File(CurationService.config
                .getMetExtrConfUploadPath()), configId));
        this.writeMetFile(id, metadata);
        return metadata;
      }
    }
  }

  /**
   * 
   * @param id
   *          Relative path from staging root to the product
   * @param config
   *          Configuration to run this met extractor
   * @return
   * @throws MetExtractionException
   */
  protected Metadata runMetExtractor(String id, ExtractorConfig config)
      throws MetExtractionException {
    MetExtractor metExtractor = GenericMetadataObjectFactory
        .getMetExtractorFromClassName(config.getClassName());
    metExtractor.setConfigFile(config.getConfigFiles().get(0));
    return metExtractor.extractMetadata(CurationService.config
        .getStagingAreaPath()
        + "/" + id);
  }
  
  @GET
  @Path(CATALOG)
  @Produces("text/plain")
  public String getCatalogMetadata(@QueryParam("id") String id,
      @DefaultValue(FORMAT_HTML) @QueryParam("format") String format,
      @Context HttpServletRequest req, @Context HttpServletResponse res) {

      // this.sendRedirect("login.jsp", uriInfo, res);
      // Call file manager to get metadata
      Product prod;
      Metadata metadata;
      String productId = id.substring(id.lastIndexOf("/") + 1);

      try {
        prod = CurationService.config.getFileManagerClient().getProductById(
          productId);
        metadata = this.getCatalogMetadata(prod);
      } catch (Exception e) {
        return "<div class=\"error\">" + e.getMessage() + "</div>";
      }

      if (FORMAT_HTML.equals(format)) {
        return this.getMetadataAsHTML(metadata);
      }
      return this.getMetadataAsJSON(metadata).toString();
  }

  @POST
  @Path(CATALOG)
  @Consumes("application/x-www-form-urlencoded")
  @Produces("text/plain")
  public String setCatalogMetadata(MultivaluedMap<String, String> formParams,
      @FormParam("id") String id) {
    Product prod;
    Metadata metadata = this.getMetadataFromMap(formParams);
    String productId = id.substring(id.lastIndexOf("/") + 1);

    try {
      prod = CurationService.config.getFileManagerClient().getProductById(
          productId);
      this.updateCatalogMetadata(prod, metadata);
    } catch (Exception e) {
      e.printStackTrace();
      return "<div class=\"error\">" + e.getMessage() + "</div>";
    }

    return this.getMetadataAsHTML(metadata);
  }
  
  @GET
  @Path(PRODUCT_TYPE)
  @Produces("text/plain")
  public String getProductTypeMetadata(@QueryParam("id") String id,
      @DefaultValue(FORMAT_HTML) @QueryParam("format") String format,
      @Context HttpServletRequest req, @Context HttpServletResponse res) {

    // this.sendRedirect("login.jsp", uriInfo, res);

    Metadata metadata;
    String[] idParts = id.split("/");
    String policy = idParts[1];
    String productType = idParts[2];
    try {
      metadata = getProductTypeMetadataForPolicy(policy, productType);
    } catch (Exception e) {
      return "<div class=\"error\">" + e.getMessage() + "</div>";
    }

    if (FORMAT_HTML.equals(format)) {
      return this.getMetadataAsHTML(metadata);
    }
    return this.getMetadataAsJSON(metadata).toString();
  }
  

  @POST
  @Path(PRODUCT_TYPE)
  @Consumes("application/x-www-form-urlencoded")
  @Produces("text/plain")
  public String setProductTypeMetadata(MultivaluedMap<String, String> formParams) {
    String[] idParts = formParams.getFirst("id").split("/");
    String policy = idParts[1];
    String productType = idParts[2];
    try {
    this.writeProductTypeMetadata(policy, productType, this
        .getMetadataFromMap(formParams));
    } catch (Exception e) {
      return "<div class=\"error\">" + e.getMessage() + "</div>";
    }
    return "";
  }

  @POST
  @Path(STAGING)
  @Consumes("application/x-www-form-urlencoded")
  @Produces("text/plain")
  public String setStagingMetadata(MultivaluedMap<String, String> formParams) {
    try {
      this.writeMetFile(formParams.getFirst("id"), this
          .getMetadataFromMap(formParams));
    } catch (Exception e) {
      return "<div class=\"error\">" + e.getMessage() + "</div>";
    }
    return "";
  }

  @GET
  @Path("staging/info")
  @Produces("text/plain")
  public String getMetadataInfo(@QueryParam("id") String id) {

      return "Staging met info";
  }
  

  private JSONObject getMetadataAsJSON(Metadata metadata) {
    return JSONObject.fromObject(metadata.getHashtable());
  }

  private Metadata getMetadataFromJSON(String metadataJSON) {
    JSONObject json = (JSONObject) JSONSerializer.toJSON(metadataJSON);
    Metadata metadata = new Metadata();

    Set<String> keys = json.keySet();
    for (String key : keys) {
      List values = (List) JSONSerializer.toJava((JSONArray) json.get(key));
      metadata.addMetadata(key, values);
    }

    return metadata;
  }
  
  private Metadata getMetadataFromMap(MultivaluedMap<String, String> formParams) {
    Metadata metadata = new Metadata();
    
    for (String key : formParams.keySet()) {
      if (key.startsWith("metadata.")) {
        String newKey = key.substring(key.indexOf('.') + 1);
        for (String value : formParams.get(key)) {
          metadata.addMetadata(newKey, value);
        }
      }
    }
    
    return metadata;
  }
  
  protected String getMetadataAsHTML(Metadata metadata) {
    if (metadata == null) {
      return "<table></table>";
    }

    StringBuffer html = new StringBuffer();

    html.append("<table>\r\n");
    for (String key : (Set<String>) metadata.getHashtable().keySet()) {
      html.append(" <tr>\r\n");
      html.append("  <th>").append(key).append("</th>\r\n");
      html.append("  <td class=\"").append(key).append("\">");
      List<String> values = metadata.getAllMetadata(key);
      for (Iterator<String> i = values.iterator(); i.hasNext();) {
        html.append("<span>").append(i.next()).append("</span>");
        if (i.hasNext()) {
          html.append(", ");
        }
      }
      for (String value : (List<String>) metadata.getAllMetadata(key)) {
      }
      html.append("</td>\r\n");
      html.append(" </tr>\r\n");
    }
    html.append("</table>\r\n");

    return html.toString();
  }
  

  /**
   * Reads a {@link Metadata} object from a String representation of a .met
   * {@link File}.
   * 
   * @param file
   *          The full path to the .met {@link File}.
   * @return The read-in CAS {@link Metadata} object.
   * @throws InstantiationException
   * @throws InstantiationException
   *           If there is an error instantiating the {@link Metadata} class.
   * @throws IOException
   * @throws FileNotFoundException
   * @throws FileNotFoundException
   *           If the .met {@link File} is not found.
   * @throws IOException
   *           If there is an IO problem opening the met file.
   */
  public Metadata readMetFile(String file) throws InstantiationException,
      FileNotFoundException, IOException {
    SerializableMetadata metadata = new SerializableMetadata("UTF-8", false);
    metadata.loadMetadataFromXmlStream(new FileInputStream(config
        .getMetAreaPath()
        + "/" + file));

    return metadata;
  }

  /**
   * Retrieves the cataloged {@link Metadata} associated with a {@link Product}.
   * 
   * @param product
   *          The {@link Product} to obtain cataloged {@link Metadata} for.
   * @return The cataloged {@link Metadata} for {@link Product}.
   * @throws CatalogException
   *           If there is an error talking to the CAS File Manager
   *           {@link Catalog}.
   */
  public Metadata getCatalogMetadata(Product product) throws CatalogException {
    return CurationService.config.getFileManagerClient().getMetadata(
        CurationService.config.getFileManagerClient().getProductById(
            product.getProductId()));
  }

  /**
   * Writes a CAS {@link Metadata} {@link File} using the given identifier.
   * 
   * @param id
   *          The identifier of the .met file to write.
   * @param metadata
   *          The {@link Metadata} object to persist and write to a {@link File}
   *          .
   * @throws FileNotFoundException
   *           If the .met {@link File} cannot be written.
   * @throws IOException
   *           If there is an IO exception writing the {@link File}.
   */
  public void writeMetFile(String id, Metadata metadata)
      throws FileNotFoundException, IOException {
    SerializableMetadata serMet = new SerializableMetadata(metadata, "UTF-8",
        false);
    serMet.writeMetadataToXmlStream(new FileOutputStream(new File(config
        .getMetAreaPath(), id + config.getMetExtension())));
  }

  /**
   * Updates the cataloged {@link Metadata} for a {@link Product} in the CAS
   * File Manager.
   * 
   * @param product
   *          The {@link Product} to update {@link Metadata} for.
   * @param metadata
   *          The new {@link Metadata} to persist into the {@link Catalog}.
   * @throws CatalogException
   *           If any error occurs during the update.
   * @throws IOException
   * @throws FileNotFoundException
   */
  public void updateCatalogMetadata(Product product, Metadata newMetadata)
      throws CatalogException, FileNotFoundException, IOException {
    System.getProperties().load(
        new FileInputStream(CurationService.config.getFileMgrProps()));
    Catalog catalog = GenericFileManagerObjectFactory
        .getCatalogServiceFromFactory("gov.nasa.jpl.oodt.cas.curation.util.CuratorLuceneCatalogFactory");
    
    Metadata oldMetadata = catalog.getMetadata(product);
    List<Reference> references = catalog.getProductReferences(product);
    Product newProduct = new Product(product.getProductName(), product
        .getProductType(), product.getProductStructure(), product
        .getTransferStatus(), product.getProductReferences());
    // Constructor is bugged and doesn't set transfer status
    newProduct.setTransferStatus(product.getTransferStatus());
    catalog.removeMetadata(oldMetadata, product);
    catalog.removeProduct(product);
    newProduct.setProductId(product.getProductId());
    catalog.addProduct(newProduct);
    newProduct.setProductReferences(references);
    catalog.addProductReferences(newProduct);
    catalog.addMetadata(newMetadata, newProduct);
  }


  private Metadata getProductTypeMetadataForPolicy(String policy,
      String productTypeName) throws MalformedURLException,
      InstantiationException, RepositoryManagerException {
    String rootPolicyPath = this.cleanse(CurationService.config
        .getPolicyUploadPath());
    String policyPath = new File(rootPolicyPath + policy).toURL()
        .toExternalForm();
    String[] policies = { policyPath };
    /*XMLRepositoryManager repMgr = new XMLRepositoryManager(Arrays
      .asList(policies));*/
    ProductType productType = this.config.getFileManagerClient().getProductTypeByName(productTypeName);
    //repMgr.getProductTypeByName(productTypeName);
    
    return productType.getTypeMetadata();
  }
  
  private Metadata writeProductTypeMetadata(String policy,
      String productTypeName, Metadata metadata) throws Exception {
    String rootPolicyPath = this.cleanse(CurationService.config
        .getPolicyUploadPath());
    String policyPath = new File(rootPolicyPath + policy).toURL()
        .toExternalForm();
    String[] policies = { policyPath };
    XMLRepositoryManager repMgr = new XMLRepositoryManager(Arrays
        .asList(policies));

    ProductType productType = repMgr.getProductTypeByName(productTypeName);
    productType.setTypeMetadata(metadata);
    
    CurationXmlStructFactory.writeProductTypeXmlDocument(repMgr
        .getProductTypes(), rootPolicyPath + policy + "/product-types.xml");

    // refresh the config on the fm end
    CurationService.config.getFileManagerClient().refreshConfigAndPolicy();
    
    return productType.getTypeMetadata();
  }
  
  private String cleanse(String origPath) {
    String retStr = origPath;
    if (!retStr.endsWith("/")) {
      retStr += "/";
    }
    return retStr;
  }
}
