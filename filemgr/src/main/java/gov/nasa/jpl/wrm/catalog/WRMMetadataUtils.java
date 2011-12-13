//Copyright (c) 2010, California Institute of Technology.
//ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
//
//$Id$

package gov.nasa.jpl.wrm.catalog;

import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import gov.nasa.jpl.oodt.cas.metadata.Metadata;

/**
 * WRMMetadataUtils
 * 
 * Provides a container for utility functions pertaining to the manipulation of
 * metadata elements by the WRMCatalog class.
 * 
 * @author ahart, mattmann
 * 
 */
public final class WRMMetadataUtils {

  public static Logger LOG = Logger.getLogger(WRMMetadataUtils.class.getName());

  /**
   * getMetadataSubset
   * 
   * Returns the subset of metadata keys in the provided Metadata object that
   * match against the regular expression specified in pattern. Note that
   * complete match is not required for success. This function utilizes the
   * 'lookingAt()' function of the java.util.regex.Matcher class to determine
   * whether the candidate string contains the pattern as a substring when
   * starting from the zeroth index (the beginning).
   * 
   * @param m
   *          The Metadata object containing keys from which a subset will be
   *          extracted
   * @param pattern
   *          The regular expression to use in determining matching keys
   * @return A Metadata object containing only those keys which matched
   *         'pattern'
   */
  public static Metadata getMetadataSubset(Metadata m, Pattern pattern) {

    Metadata subset = new Metadata();

    for (Object key : m.getHashtable().keySet()) {

      Matcher matcher = pattern.matcher((String) key);
      if (matcher.lookingAt()) {
        subset.addMetadata((String) key, m.getMetadata((String) key));
      }
    }

    return subset;
  }
}
