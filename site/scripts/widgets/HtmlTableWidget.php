<?php
  /**
   * Copyright (c) 2010, California Institute of Technology.
   * ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
   * 
   * $Id$
   * 
   * 
   * OODT Balance
   * Web Application Base Framework
   * 
   * An implementation of IApplicationWidget that provides the ability
   * to rapidly build an HTML table in a view.
   * 
   * Notes:
   *  - addColumn can only be called before the first call to addRow (in other
   *    words, build all your columns first and then populate the table with rows).
   *    
   * Usage:
   * 
   * $tableWidget = $app->createWidget('HtmlTableWidget');
   * $tableWidget->addColumn('Col1');
   * $tableWidget->addColumn('Col2');
   * $tableWidget->addRow(array("column1Value","column2Value"));
   * 
   * <!-- render the table -->
   * <?php echo $tableWidget->render();?>
   * 
   * @author ahart
   * 
   */
class HtmlTableWidget 
  implements Org_Apache_Oodt_Balance_Interfaces_IApplicationWidget {
  
  public $headers;
  
  public $rows;
  
  public $canAddColumns;
  
  public function __construct($options = array()) {
    $this->canAddColumns = true;
  }
  
  public function addColumn($label) {
    if ($this->canAddColumns) {
      $this->headers[] = array('label' => $label);
    }
  }
  
  public function addRow($data) {
    $this->canAddColumns = false;
    $this->rows[] = $data;
  }
  
  public function render($bEcho = false) {
    
    $r = "<table>";
    
    // Head
    $r .= "<thead><tr>";
    foreach ($this->headers as $col) {
      $r .= "<th>{$col['label']}</th>";
    }
    $r .= "</tr></thead>";
    
    // Body
    $r .= "<tbody>";
    foreach ($this->rows as $row) {
      $r .= "<tr><td>" . implode("</td><td>",$row) . "</td></tr>";
    }
    $r .= "</tbody>";
    
    $r .= "</table>";
    
    return $r;
  }
}