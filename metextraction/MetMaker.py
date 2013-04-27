'''File Manager Metadata Creation Class
This can be imported into a metadata extraction script to help with many of the
simple and often repeated processes, such as creating XML headers and footers
as well as extraction of data.

Author:  Cameron Goodale  cgoodale@jpl.nasa.gov
Created:  06-JAN-2012
Updated:  06-JAN-2012

'''
import sys


class CAS_Met(object):
    
    #setup the default values that each CAS_Met object needs
    def __init__(self):
        self.cas_xml = '<?xml version="1.0" encoding="UTF-8"?>\n <cas:metadata xmlns:cas="http://oodt.apache.org/1.0/cas">\n'
        self.cas_footer = '</cas:metadata>'
        self.cas_key_start = '<keyval>\n \t<key>'
        self.cas_key_end = '</key>\n'
        self.cas_val_start = '\t<val>'
        self.cas_val_end = '</val>\n'
        self.cas_keyval_end = '</keyval>\n'
        self.metadata = [self.cas_xml,self.cas_footer]
        
    def add_met(self, key, val_list):
        met_key = self.cas_key_start+str(key)+self.cas_key_end
        met_val = self.val_maker(val_list)
        met_combo = met_key+met_val+self.cas_keyval_end
        self.metadata.insert(len(self.metadata)-1, met_combo)
        
    def val_maker(self,v_list):
        val_holder = []
        for v in v_list:
            #Create the met_val
            met_val = self.cas_val_start+str(v)+self.cas_val_end
            #add the met_val to the val_holder list
            val_holder.append(met_val)
        
        return ''.join(val_holder)
        
    def write_met(self,output_path):
        try:
            output = open(output_path,"w")
            met = ''.join(self.metadata)
            output.write(met)
        except Exception, e:
            print str(e)