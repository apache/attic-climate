//Copyright (c) 2009, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id: PolicyResource.java 7000 2009-10-26 16:39:11Z pramirez $

package gov.nasa.jpl.oodt.cas.curation.service;

//OODT imports
import gov.nasa.jpl.oodt.cas.curation.util.HTMLEncode;
import gov.nasa.jpl.oodt.cas.filemgr.structs.Product;
import gov.nasa.jpl.oodt.cas.filemgr.structs.ProductPage;
import gov.nasa.jpl.oodt.cas.filemgr.structs.ProductType;
import gov.nasa.jpl.oodt.cas.filemgr.structs.Query;
import gov.nasa.jpl.oodt.cas.filemgr.structs.exceptions.RepositoryManagerException;

//JDK imports
import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;

//JAX-RS imports
import javax.servlet.ServletContext;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.ws.rs.DefaultValue;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.UriInfo;
import com.sun.jersey.spi.resource.Singleton;

//JSON imports
import net.sf.json.JSONObject;

@Path("policy")
@Singleton
public class PolicyResource extends CurationService {

  @Context
  UriInfo uriInfo;

  private static final long serialVersionUID = -3757481221589264709L;

  private static final Logger LOG = Logger.getLogger(PolicyResource.class
      .getName());

  private static final FilenameFilter DIR_FILTER = new FilenameFilter() {

    public boolean accept(File dir, String name) {
      return new File(dir, name).isDirectory()
          && !new File(dir, name).getName().startsWith(".");
    }
  };
  
  public PolicyResource(@Context ServletContext context){
    
  }

  @GET
  @Path("browse")
  @Produces("text/plain")
  public String browseCatalog(
      @QueryParam("path") @DefaultValue("/") String path,
      @DefaultValue(FORMAT_HTML) @QueryParam("format") String format,
      @DefaultValue("1") @QueryParam("pageNum") Integer pageNum,
      @Context HttpServletRequest req, @Context HttpServletResponse res)
      throws IOException {
    
    // TODO: Send a not authorized response if not logged in. This should be a
    // utility method as a part of CurationService that every service interface
    // calls.

    String[] pathToks = tokenizeVirtualPath(path);
    String policy = null;
    String productType = null;

    if (pathToks == null) {
      LOG.log(Level.WARNING, "malformed path token string: "
          + Arrays.asList(pathToks));
      return "";
    }

    policy = pathToks.length > 0 ? pathToks[0]:null;
    productType = pathToks.length > 1 ? pathToks[1] : null;

    if (policy != null) {
      if (productType != null) {
        return getProductsForProductType(policy, productType, format, pageNum);
      } else {
        return getProductTypesForPolicy(policy, format);
      }
    } else {
      return getPolicies(format);
    }

  }
  
  private String getProductsForProductType(String policy,
      String productTypeName,
      String format, int pageNum) {
    
    ProductType productType;
    ProductPage page;
    try {
      productType = this.config.getFileManagerClient().getProductTypeByName(
          productTypeName);
      page = this.config.getFileManagerClient().pagedQuery(new Query(),
          productType, pageNum);
    } catch (Exception e) {
      e.printStackTrace();
      LOG.log(Level.WARNING, "Unable to obtain products for product type: ["
          + productTypeName + "]: Message: " + e.getMessage());
      return "";
    }

    if (format.equals(FORMAT_HTML)) {
      return encodeProductsAsHTML(page, policy, productTypeName);
    } else if (format.equals(FORMAT_JSON)) {
      return encodeProductsAsJSON(page, policy, productTypeName);
    } else {
      return UNKNOWN_OUT_FORMAT;
    }
  }
  
  private String encodeProductsAsHTML(ProductPage page, String policy,
      String productTypeName) {
    StringBuffer html = new StringBuffer();
    html.append("<ul class=\"fileTree\" >\r\n");
    
    for (Product product : page.getPageProducts()) {
      html.append(" <li class=\"file\">");
      html.append("<a href=\"#\" rel=\"/");
      html.append(policy);
      html.append("/");
      html.append(productTypeName);
      html.append("/");
      html.append(product.getProductId());
      html.append("\">");
      html.append(product.getProductName());
      html.append("</a>");
      html.append("</li>\r\n");
    }

    html.append("</ul>");
    return html.toString();
  }
  
  private String encodeProductsAsJSON(ProductPage page, String policy,
      String productTypeName) {
    return "NOT IMPLENTED YET";
  }

  private String getPolicies(String format) {
    String policyPath = this.cleanse(CurationService.config
        .getPolicyUploadPath());
    String[] policyDirs = new File(policyPath).list(DIR_FILTER);

    if (format.equals(FORMAT_HTML)) {
      return encodePoliciesAsHTML(policyDirs);
    } else if (format.equals(FORMAT_JSON)) {
      return encodePoliciesAsJSON(policyDirs);
    } else {
      return UNKNOWN_OUT_FORMAT;
    }

  }

  private String getProductTypesForPolicy(String policy, String format) {
    String[] typeNames = null;
    try {
      typeNames = this.getProductTypeNamesForPolicy(policy);
    } catch (Exception e) {
      e.printStackTrace();
      LOG.log(Level.WARNING,
          "Unable to obtain product type names for policy: [" + policy
              + "]: Message: " + e.getMessage());
      return "";
    }

    if (format.equals(FORMAT_HTML)) {
      return encodeProductTypesAsHTML(policy, typeNames);
    } else if (format.equals(FORMAT_JSON)) {
      return encodeProductTypesAsJSON(policy, typeNames);
    } else {
      return UNKNOWN_OUT_FORMAT;
    }

  }

  private String encodePoliciesAsHTML(String[] policyDirs) {
    StringBuffer out = new StringBuffer();
    out.append("<ul class=\"fileTree\" >");
    for (String policy : policyDirs) {
      out.append("<li class=\"directory collapsed\"><a href=\"#\" rel=\"/");
      out.append(HTMLEncode.encode(policy));
      out.append("/\">");
      out.append(HTMLEncode.encode(policy));
      out.append("</a></li>");
    }
    out.append("</ul>");
    return out.toString();
  }

  private String encodePoliciesAsJSON(String[] policyDirs) {
    Map<String, String> retMap = new HashMap<String, String>();
    for (String policyDir : policyDirs) {
      retMap.put("policy", policyDir);
    }
    JSONObject resObj = new JSONObject();
    resObj.put("policies", retMap);
    resObj.put("succeed", true);
    return resObj.toString();
  }

  private String encodeProductTypesAsHTML(String policy, String[] typeNames) {
    StringBuffer out = new StringBuffer();
    out.append("<ul class=\"fileTree\" >");
    for (String type : typeNames) {
      out
          .append("<li class=\"directory collapsed productType\"><a href=\"#\" rel=\"/");
      out.append(HTMLEncode.encode(policy));
      out.append("/");
      out.append(HTMLEncode.encode(type));
      out.append("/\">");
      out.append(HTMLEncode.encode(type));
      out.append("</a></li>");
    }

    out.append("</ul>");
    return out.toString();
  }

  private String encodeProductTypesAsJSON(String policy, String[] typeNames) {
    Map<String, Object> retMap = new HashMap<String, Object>();
    retMap.put("policy", policy);
    List<Map<String, String>> typeList = new Vector<Map<String, String>>();
    for (String typeName : typeNames) {
      Map<String, String> typeMap = new HashMap<String, String>();
      typeMap.put("name", typeName);
      typeList.add(typeMap);
    }
    retMap.put("productTypes", typeList);
    JSONObject resObj = new JSONObject();
    resObj.putAll(retMap);
    return resObj.toString();
  }

  private String[] getProductTypeNamesForPolicy(String policy)
      throws MalformedURLException, InstantiationException,
      RepositoryManagerException {
    List<ProductType> types = this.config.getFileManagerClient().getProductTypes();
    String[] typeNames = new String[types.size()];
    int i = 0;
    for (ProductType type : types) {
      typeNames[i] = type.getName();
      i++;
    }

    return typeNames;
  }

  private String cleanse(String origPath) {
    String retStr = origPath;
    if (!retStr.endsWith("/")) {
      retStr += "/";
    }
    return retStr;
  }

  private String[] tokenizeVirtualPath(String path) {
    String vPath = path;
    if (vPath.startsWith("/") && vPath.length() != 1) {
      vPath = vPath.substring(1);
    }
    String[] pathToks = vPath.split("/");
    LOG.log(Level.INFO, "origPath: ["+path+"]");
    LOG.log(Level.INFO, "pathToks: "+Arrays.asList(pathToks));
    return pathToks;
  }

}
